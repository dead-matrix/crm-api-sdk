from __future__ import annotations

import asyncio
import sys
import pathlib
from typing import Any, Dict

import httpx
import pytest

# Ensure repo root on path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from conftest import success_response, error_response
from crm_api.client import CRMApiClient
from crm_api.exceptions import ConfigError
from crm_api.models import CreateUserInput, UpdateUserInput


def make_handler() -> httpx.MockTransport:
    state: Dict[str, Any] = {
        "auth_calls": 0,
        "users_get_calls": 0,
    }

    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        # Auth issuance
        if path.startswith("/api/staff/") and path.endswith("/auth") and req.method == "POST":
            state["auth_calls"] += 1
            data = {
                "token": f"JWT{state['auth_calls']}",
                "expires_at": "2030-01-01T00:00:00+00:00",
            }
            return httpx.Response(200, json={"status": "success", "data": data})

        # Users endpoints
        if path == "/api/users" and req.method == "POST":
            data = {
                "created": True,
                "user_id": 1,
                "full_name": "John",
                "username": "j",
                "bot_id": 1,
                "refer": None,
                "date_reg": "2026-04-29T12:00:00+00:00",
            }
            return httpx.Response(200, json={"status": "success", "data": data})

        if path.startswith("/api/users/") and req.method == "PUT":
            import json
            user_id = int(path.split("/")[-1])
            body = json.loads(req.content.decode("utf-8"))
            data = {"user_id": user_id, "full_name": body.get("full_name"), "username": body.get("username")}
            return httpx.Response(200, json={"status": "success", "data": data})

        if path.startswith("/api/users/") and req.method == "GET":
            state["users_get_calls"] += 1
            # Force a single 401 to verify JWT refresh logic
            if state["users_get_calls"] == 1:
                return httpx.Response(401, json={"status": "error", "message": "unauthorized"})
            user_id = int(path.split("/")[-1])
            data = {
                "user_id": user_id,
                "full_name": "John Doe",
                "username": "johndoe",
                "status": "active",
                "bots_info": [
                    {
                        "bot_id": 1,
                        "bot_name": "MainBot",
                        "registered": "2024-10-01T00:00:00+00:00",
                        "refer": None,
                        "access": None,
                        "access_end": None,
                    }
                ],
            }
            return httpx.Response(200, json={"status": "success", "data": data})

        return httpx.Response(404, json={"status": "error", "message": f"not found: {path}"})

    return httpx.MockTransport(handler)


class TestUsers:
    @pytest.mark.asyncio
    async def test_users_crud_and_auth_refresh(self):
        transport = make_handler()
        async with CRMApiClient(base_url="https://example", staff_id=123, service_token="T", transport=transport) as c:
            # create
            created = await c.create_user(CreateUserInput(user_id=1, full_name="John", username="j", bot_id=1))
            assert created.created is True
            assert created.user_id == 1
            assert created.full_name == "John"
            assert created.bot_id == 1
            assert created.date_reg is not None  # parsed
            # update
            upd = await c.update_user(1, UpdateUserInput(full_name="John X", username="jx"))
            assert upd.user_id == 1 and upd.full_name == "John X" and upd.username == "jx"
            # get with forced 401 then refresh
            user = await c.get_user(1)
            assert user.user_id == 1
            assert user.full_name == "John Doe"
            assert user.bots_info and user.bots_info[0].bot_id == 1


class TestCreateUserIdempotency:
    @pytest.mark.asyncio
    async def test_create_user_first_time_returns_created_true(self, client_factory):
        """Новая регистрация — created=True + поля заполнены."""
        mock_data = {
            "created": True,
            "user_id": 999,
            "full_name": "Charlie",
            "username": "charlie",
            "bot_id": 1,
            "refer": None,
            "date_reg": "2026-04-29T12:00:00+00:00",
        }
        routes = {"POST /api/users": lambda req: success_response(mock_data)}
        async with client_factory(routes) as client:
            result = await client.create_user(CreateUserInput(
                user_id=999, full_name="Charlie", username="charlie", bot_id=1,
            ))
            assert result.created is True
            assert result.user_id == 999
            assert result.full_name == "Charlie"
            assert result.username == "charlie"
            assert result.bot_id == 1
            assert result.refer is None
            assert result.date_reg is not None

    @pytest.mark.asyncio
    async def test_create_user_idempotent_returns_existing(self, client_factory):
        """
        Регистрация (user_id, bot_id) уже существовала — created=False
        и API возвращает существующие данные (не payload).
        """
        existing = {
            "created": False,
            "user_id": 12345,
            "full_name": "OldName",
            "username": "oldun",
            "bot_id": 1,
            "refer": "oldref",
            "date_reg": "2026-01-15T12:00:00+00:00",
        }
        routes = {"POST /api/users": lambda req: success_response(existing)}
        async with client_factory(routes) as client:
            # Шлём ДРУГОЙ full_name/refer — но API вернёт старые значения.
            result = await client.create_user(CreateUserInput(
                user_id=12345, full_name="NewName", username="newun", bot_id=1, refer="newref",
            ))
            assert result.created is False
            assert result.full_name == "OldName"
            assert result.refer == "oldref"
            assert result.date_reg is not None


class TestListUsers:
    @pytest.mark.asyncio
    async def test_list_users_returns_paginated_items(self, client_factory):
        mock_data = {
            "bot_id": 1,
            "limit": 50,
            "offset": 10,
            "count": 2,
            "items": [
                {
                    "user_id": 101, "full_name": "Alice", "username": "alice",
                    "date_reg": "2026-04-01T10:00:00+00:00", "refer": None,
                    "restricted": False,
                },
                {
                    "user_id": 102, "full_name": "Bob", "username": None,
                    "date_reg": "2026-04-02T11:00:00+00:00", "refer": "ref-x",
                    "restricted": True,
                },
            ],
        }
        captured: dict = {}

        def _handler(req):
            for k, v in req.url.params.items():
                captured[k] = v
            return success_response(mock_data)

        routes = {"GET /api/users": _handler}
        async with client_factory(routes) as client:
            result = await client.list_users(bot_id=1, limit=50, offset=10)

            # Verify query params are sent correctly
            assert captured == {"bot_id": "1", "limit": "50", "offset": "10"}

            # Result shape
            assert result.bot_id == 1
            assert result.limit == 50
            assert result.offset == 10
            assert result.count == 2
            assert len(result.items) == 2

            alice, bob = result.items
            assert alice.user_id == 101
            assert alice.full_name == "Alice"
            assert alice.username == "alice"
            assert alice.restricted is False
            assert alice.date_reg is not None

            assert bob.user_id == 102
            assert bob.username is None
            assert bob.refer == "ref-x"
            assert bob.restricted is True

    @pytest.mark.asyncio
    async def test_list_users_default_params(self, client_factory):
        """Дефолты: limit=100_000, offset=0."""
        captured: dict = {}

        def _handler(req):
            for k, v in req.url.params.items():
                captured[k] = v
            return success_response({"bot_id": 1, "limit": 100000, "offset": 0, "count": 0, "items": []})

        routes = {"GET /api/users": _handler}
        async with client_factory(routes) as client:
            result = await client.list_users(bot_id=1)
            assert captured["limit"] == "100000"
            assert captured["offset"] == "0"
            assert result.items == []

    @pytest.mark.asyncio
    async def test_list_users_validation_errors(self, client_factory):
        """ConfigError при некорректных параметрах — без HTTP-вызова."""
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.list_users(bot_id=0)
            with pytest.raises(ConfigError):
                await client.list_users(bot_id=1, limit=0)
            with pytest.raises(ConfigError):
                await client.list_users(bot_id=1, offset=-1)

    @pytest.mark.asyncio
    async def test_list_users_restricted_defaults_false_when_missing(self, client_factory):
        """Если API не вернёт поле restricted (старая версия) — дефолт False."""
        mock_data = {
            "bot_id": 1, "limit": 100, "offset": 0, "count": 1,
            "items": [{
                "user_id": 1, "full_name": "X", "username": None,
                "date_reg": None, "refer": None,
                # restricted намеренно отсутствует
            }],
        }
        routes = {"GET /api/users": lambda req: success_response(mock_data)}
        async with client_factory(routes) as client:
            result = await client.list_users(bot_id=1)
            assert result.items[0].restricted is False

