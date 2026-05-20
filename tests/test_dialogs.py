"""Tests for DialogsAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestDialogsAPI:
    @pytest.mark.asyncio
    async def test_get_dialogs_success(self, client_factory):
        """Test get_dialogs returns properly mapped DialogItem list."""
        mock_data = {
            "dialogs": [
                {"user_id": 100, "full_name": "User One", "has_active_subscription": True, "status": "open", "status_color": "#FF5733"},
                {"user_id": 200, "full_name": "User Two", "has_active_subscription": False, "status": "pending", "status_color": None},
            ]
        }
        routes = {
            "GET /api/dialogs/{department}": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_dialogs("support")

            assert len(result) == 2
            assert result[0].user_id == 100
            assert result[0].full_name == "User One"
            assert result[0].has_active_subscription is True
            assert result[0].status == "open"
            assert result[0].status_color == "#FF5733"

            assert result[1].user_id == 200
            assert result[1].full_name == "User Two"
            assert result[1].has_active_subscription is False
            assert result[1].status == "pending"
            assert result[1].status_color is None

    @pytest.mark.asyncio
    async def test_get_dialogs_empty(self, client_factory):
        """Test get_dialogs with empty dialogs list."""
        routes = {
            "GET /api/dialogs/{department}": lambda req: success_response({"dialogs": []}),
        }
        async with client_factory(routes) as client:
            result = await client.get_dialogs("sales")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_statuses_success(self, client_factory):
        """Test get_statuses returns StatusesResult with statuses list."""
        mock_data = {
            "department_id": 1,
            "default_status_id": 10,
            "statuses": [
                {"id": 10, "title": "Новый", "color": "#4CAF50"},
                {"id": 20, "title": "В работе", "color": "#2196F3"},
                {"id": 30, "title": "Закрыт", "color": None},
            ]
        }
        routes = {
            "GET /api/dialogs/statuses/{department_id}": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_statuses(department_id=1)

            assert result.department_id == 1
            assert result.default_status_id == 10
            assert len(result.statuses) == 3
            assert result.statuses[0].id == 10
            assert result.statuses[0].title == "Новый"
            assert result.statuses[0].color == "#4CAF50"
            assert result.statuses[1].color == "#2196F3"
            assert result.statuses[2].color is None

    @pytest.mark.asyncio
    async def test_get_statuses_invalid_department_id(self, client_factory):
        """Test get_statuses raises ConfigError for invalid department_id."""
        from crm_api.exceptions import ConfigError
        
        routes = {}
        async with client_factory(routes) as client:
            with pytest.raises(ConfigError, match="department_id must be positive"):
                await client.get_statuses(department_id=0)

    @pytest.mark.asyncio
    async def test_change_dialog_status_success(self, client_factory):
        """Test change_dialog_status returns ChangeStatusResult."""
        mock_data = {"status": "updated"}
        routes = {
            "POST /api/dialogs/status": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.change_dialog_status(user_id=100, status_id=20)
            assert result.status == "updated"

    @pytest.mark.asyncio
    async def test_change_dialog_status_invalid_ids(self, client_factory):
        """Test change_dialog_status raises ConfigError for invalid IDs."""
        from crm_api.exceptions import ConfigError

        routes = {}
        async with client_factory(routes) as client:
            with pytest.raises(ConfigError, match="user_id must be positive"):
                await client.change_dialog_status(user_id=0, status_id=1)
            with pytest.raises(ConfigError, match="status_id must be positive"):
                await client.change_dialog_status(user_id=1, status_id=0)

    @pytest.mark.asyncio
    async def test_change_dialog_status_clear_sends_explicit_null(self, client_factory):
        """status_id=None → payload с явным JSON null, поле status в ответе → None."""
        captured: dict = {}
        raw_body: dict = {}

        def _handler(req):
            import json as _json
            body = _json.loads(req.content)
            captured.update(body)
            raw_body["bytes"] = req.content
            raw_body["keys"] = list(body.keys())
            return success_response({"status": None})

        routes = {"POST /api/dialogs/status": _handler}
        async with client_factory(routes) as client:
            result = await client.change_dialog_status(user_id=100, status_id=None)
            assert result.status is None

        assert captured == {"user_id": 100, "status_id": None}
        assert "status_id" in raw_body["keys"], "status_id must be present in payload"
        assert b'"status_id"' in raw_body["bytes"]
        assert b'null' in raw_body["bytes"]

    @pytest.mark.asyncio
    async def test_clear_dialog_status_alias_sends_explicit_null(self, client_factory):
        """clear_dialog_status шлёт явный status_id: null (паритет с Go SDK)."""
        captured: dict = {}
        raw_body: dict = {}

        def _handler(req):
            import json as _json
            body = _json.loads(req.content)
            captured.update(body)
            raw_body["bytes"] = req.content
            return success_response({"status": None})

        routes = {"POST /api/dialogs/status": _handler}
        async with client_factory(routes) as client:
            result = await client.clear_dialog_status(user_id=42)
            assert result.status is None

        assert captured == {"user_id": 42, "status_id": None}
        assert b'"status_id"' in raw_body["bytes"]
        assert b'null' in raw_body["bytes"]

    @pytest.mark.asyncio
    async def test_search_dialogs_null_status_preserved(self, client_factory):
        """
        Сервер может вернуть status/status_color=null (диалог без статуса
        в департаменте без default_status). SDK не должен превращать None
        в строку 'None'.
        """
        mock_data = {
            "dialogs": [
                {
                    "user_id": 1, "full_name": "User",
                    "has_active_subscription": False,
                    "status": None, "status_color": None,
                }
            ],
            "limit": 50, "offset": 0,
        }
        routes = {"GET /api/dialogs/{department}/search": lambda req: success_response(mock_data)}
        async with client_factory(routes) as client:
            result = await client.search_dialogs("sales", q="user")
            assert result.dialogs[0].status is None
            assert result.dialogs[0].status_color is None

    @pytest.mark.asyncio
    async def test_transfer_dialog_success(self, client_factory):
        """Test transfer_dialog returns TransferDialogResult."""
        mock_data = {"transferred": True}
        routes = {
            "POST /api/dialogs/transfer": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.transfer_dialog(user_id=100, to_department="sales")
            assert result.transferred is True

    @pytest.mark.asyncio
    async def test_transfer_dialog_not_transferred(self, client_factory):
        """Test transfer_dialog when transfer fails."""
        mock_data = {"transferred": False}
        routes = {
            "POST /api/dialogs/transfer": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.transfer_dialog(user_id=100, to_department="billing")
            assert result.transferred is False

