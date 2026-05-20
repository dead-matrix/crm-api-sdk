"""Tests for SubscriptionsAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response
from crm_api.models import AddAccessInput


class TestSubscriptionsAPI:
    @pytest.mark.asyncio
    async def test_add_access_body_omits_none_fields(self, client_factory):
        """
        Wire-паритет с Go SDK: опциональные None-поля не отправляются
        как explicit null, а пропускаются. Сервер принимает оба варианта,
        но единая форма упрощает диагностику.
        """
        captured = {}

        def _handler(req):
            import json as _json
            body = _json.loads(req.content)
            captured["body"] = body
            captured["bytes"] = req.content
            return success_response({
                "created": True, "id": 1, "user_id": 1, "bot_id": 1,
                "action": "add", "action_date": None, "access_end": None,
            })

        routes = {"POST /api/access/add": _handler}
        async with client_factory(routes) as client:
            await client.add_access(AddAccessInput(user_id=1, bot_id=1, action="add"))

        assert captured["body"] == {"user_id": 1, "bot_id": 1, "action": "add"}
        # Не должно быть explicit null'ов — паритет с Go omitempty.
        assert b"null" not in captured["bytes"], (
            "опциональные поля должны опускаться, а не отправляться как null"
        )

    @pytest.mark.asyncio
    async def test_add_access_success(self, client_factory):
        """Test add_access returns AddAccessResult."""
        mock_data = {
            "created": True,
            "id": 999,
            "user_id": 123,
            "bot_id": 1,
            "action": "add",
            "action_date": "2024-01-15T10:00:00+00:00",
            "access_end": "2025-01-15T10:00:00+00:00",
        }
        routes = {
            "POST /api/access/add": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            inp = AddAccessInput(user_id=123, bot_id=1, action="add")
            result = await client.add_access(inp)
            
            assert result.created is True
            assert result.id == 999
            assert result.user_id == 123
            assert result.bot_id == 1
            assert result.action == "add"
            assert result.action_date is not None
            assert result.access_end is not None

    @pytest.mark.asyncio
    async def test_add_access_extend(self, client_factory):
        """Test add_access with extend action."""
        mock_data = {
            "created": False,
            "id": 1000,
            "user_id": 123,
            "bot_id": 1,
            "action": "extend",
            "action_date": "2024-02-01T00:00:00Z",
            "access_end": "2025-02-01T00:00:00Z",
        }
        routes = {
            "POST /api/access/add": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            inp = AddAccessInput(user_id=123, bot_id=1, action="extend")
            result = await client.add_access(inp)
            
            assert result.created is False
            assert result.action == "extend"

    @pytest.mark.asyncio
    async def test_subscriptions_history_success(self, client_factory):
        """Test subscriptions_history returns SubscriptionsHistoryResult."""
        mock_data = {
            "user_id": 123,
            "history": [
                {
                    "action": "add",
                    "bot_id": 1,
                    "access": "premium",
                    "action_date": "2024-01-01T00:00:00Z",
                    "access_end": "2025-01-01T00:00:00Z",
                    "payment": {
                        "id": 100,
                        "amount_minor": 99000,
                        "currency": "RUB",
                        "status": "paid",
                        "date_paid": "2024-01-01T00:00:00Z",
                    },
                    "staff": {"id": 1, "name": "Admin"},
                    "ref": None,
                },
                {
                    "action": "extend",
                    "bot_id": 1,
                    "access": "premium",
                    "action_date": "2024-06-01T00:00:00Z",
                    "access_end": "2025-06-01T00:00:00Z",
                    "payment": None,
                    "staff": None,
                    "ref": "promo_code",
                },
            ]
        }
        routes = {
            "GET /api/users/{user_id}/subscriptions/history": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.subscriptions_history(user_id=123)
            
            assert result.user_id == 123
            assert len(result.history) == 2
            
            h1 = result.history[0]
            assert h1.action == "add"
            assert h1.bot_id == 1
            assert h1.payment is not None
            assert h1.payment.amount_minor == 99000
            assert h1.staff is not None
            assert h1.staff.name == "Admin"
            
            h2 = result.history[1]
            assert h2.action == "extend"
            assert h2.payment is None
            assert h2.staff is None
            assert h2.ref == "promo_code"

    @pytest.mark.asyncio
    async def test_subscriptions_history_invalid_user_id(self, client_factory):
        """Test subscriptions_history raises ConfigError for invalid user_id."""
        from crm_api.exceptions import ConfigError
        
        routes = {}
        async with client_factory(routes) as client:
            with pytest.raises(ConfigError, match="user_id must be positive"):
                await client.subscriptions_history(user_id=0)

    @pytest.mark.asyncio
    async def test_access_definitions_success(self, client_factory):
        """Test access_definitions returns AccessDefinitionsResult."""
        mock_data = {
            "main": {"basic": "Базовый", "premium": "Премиум"},
            "poster": {"standard": "Стандарт", "pro": "Про"},
        }
        routes = {
            "GET /api/access/definitions": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.access_definitions()
            
            assert result.main == {"basic": "Базовый", "premium": "Премиум"}
            assert result.poster == {"standard": "Стандарт", "pro": "Про"}

    @pytest.mark.asyncio
    async def test_subscriptions_transfer_link_success(self, client_factory):
        """Test subscriptions_transfer_link returns TransferLinkResult."""
        mock_data = {"transfer_link": "https://t.me/bot?start=transfer_abc123"}
        routes = {
            "POST /api/subscriptions/transfer-link": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.subscriptions_transfer_link(user_id=123, bot_id=1)
            assert result.transfer_link == "https://t.me/bot?start=transfer_abc123"

    @pytest.mark.asyncio
    async def test_subscriptions_transfer_link_invalid_ids(self, client_factory):
        """Test subscriptions_transfer_link raises ConfigError for invalid IDs."""
        from crm_api.exceptions import ConfigError
        
        routes = {}
        async with client_factory(routes) as client:
            with pytest.raises(ConfigError, match="user_id and bot_id must be positive"):
                await client.subscriptions_transfer_link(user_id=0, bot_id=1)
            with pytest.raises(ConfigError, match="user_id and bot_id must be positive"):
                await client.subscriptions_transfer_link(user_id=1, bot_id=0)

    @pytest.mark.asyncio
    async def test_transfer_link_no_subscription_returns_result(self, client_factory):
        """
        Сервер шлёт `no_subscription` с HTTP 403. Раньше Python ловил только
        ApiError → AuthError пробрасывался. Теперь AuthError тоже ловится и
        бизнес-код доходит до Result(error_code=...).
        """
        def _handler(req):
            return httpx.Response(
                403,
                json={
                    "status": "error",
                    "message": "У пользователя отсутствует подписка для переноса",
                    "code": "no_subscription",
                },
            )

        routes = {"POST /api/subscriptions/transfer-link": _handler}
        async with client_factory(routes) as client:
            result = await client.subscriptions_transfer_link(user_id=123, bot_id=1)
            assert result.transfer_link is None
            assert result.error_code == "no_subscription"
            assert result.error_message and "подписка" in result.error_message

    @pytest.mark.asyncio
    async def test_transfer_link_not_supported_returns_result(self, client_factory):
        """501 → ApiError → Result(error_code='not_supported')."""
        def _handler(req):
            return httpx.Response(
                501,
                json={
                    "status": "error",
                    "message": "Перенос подписки для этого бота пока недоступен",
                    "code": "not_supported",
                },
            )

        routes = {"POST /api/subscriptions/transfer-link": _handler}
        async with client_factory(routes) as client:
            result = await client.subscriptions_transfer_link(user_id=1, bot_id=3)
            assert result.error_code == "not_supported"

    @pytest.mark.asyncio
    async def test_transfer_redeem_invalid_token_returns_result(self, client_factory):
        """invalid_token приходит с HTTP 400 → ValidationError → Result."""
        from crm_api.models import TransferRedeemInput

        def _handler(req):
            return httpx.Response(
                400,
                json={
                    "status": "error",
                    "message": "Ссылка переноса недействительна или повреждена",
                    "code": "invalid_token",
                },
            )

        routes = {"POST /api/subscriptions/transfer/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.subscriptions_transfer_redeem(
                TransferRedeemInput(token="TR_bad", recipient_user_id=1, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "invalid_token"

    @pytest.mark.asyncio
    async def test_transfer_redeem_same_user_returns_result(self, client_factory):
        """same_user приходит с HTTP 400 → ValidationError → Result."""
        from crm_api.models import TransferRedeemInput

        def _handler(req):
            return httpx.Response(
                400,
                json={
                    "status": "error",
                    "message": "Перенос на того же пользователя невозможен",
                    "code": "same_user",
                },
            )

        routes = {"POST /api/subscriptions/transfer/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.subscriptions_transfer_redeem(
                TransferRedeemInput(token="TR_x", recipient_user_id=1, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "same_user"

    @pytest.mark.asyncio
    async def test_transfer_redeem_recipient_has_access_returns_result(self, client_factory):
        """recipient_has_access приходит с HTTP 409 → ApiError → Result."""
        from crm_api.models import TransferRedeemInput

        def _handler(req):
            return httpx.Response(
                409,
                json={
                    "status": "error",
                    "message": "У получателя уже есть активная подписка",
                    "code": "recipient_has_access",
                },
            )

        routes = {"POST /api/subscriptions/transfer/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.subscriptions_transfer_redeem(
                TransferRedeemInput(token="TR_x", recipient_user_id=2, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "recipient_has_access"
