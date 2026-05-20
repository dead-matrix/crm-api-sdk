"""Tests for ActivationAPI: бизнес-ошибки должны превращаться в Result(success=False)."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response
from crm_api.models import ActivationRedeemInput


class TestActivationRedeem:
    @pytest.mark.asyncio
    async def test_success(self, client_factory):
        mock_data = {
            "user_id": 100,
            "bot_id": 1,
            "action": "add",
            "access": {"main": {"invite": True}},
            "access_end": "2030-01-01T00:00:00+00:00",
            "activation_code_id": 42,
            "payment_id": 7,
        }
        routes = {"POST /api/activation/redeem": lambda req: success_response(mock_data)}

        async with client_factory(routes) as client:
            result = await client.activation_redeem(
                ActivationRedeemInput(token="ACT_abc", recipient_user_id=100, bot_id=1)
            )
            assert result.success is True
            assert result.user_id == 100
            assert result.action == "add"
            assert result.error_code is None

    @pytest.mark.asyncio
    async def test_invalid_token_returns_result(self, client_factory):
        """invalid_token приходит с HTTP 400 → ValidationError → Result."""
        def _handler(req):
            return httpx.Response(
                400,
                json={"status": "error", "message": "Неверный токен", "code": "invalid_token"},
            )

        routes = {"POST /api/activation/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.activation_redeem(
                ActivationRedeemInput(token="ACT_bad", recipient_user_id=1, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "invalid_token"

    @pytest.mark.asyncio
    async def test_wrong_recipient_returns_result(self, client_factory):
        """wrong_recipient приходит с HTTP 403 → AuthError → Result."""
        def _handler(req):
            return httpx.Response(
                403,
                json={
                    "status": "error",
                    "message": "Код активации был выдан другому пользователю",
                    "code": "wrong_recipient",
                },
            )

        routes = {"POST /api/activation/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.activation_redeem(
                ActivationRedeemInput(token="ACT_x", recipient_user_id=99, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "wrong_recipient"

    @pytest.mark.asyncio
    async def test_not_found_returns_result(self, client_factory):
        """not_found приходит с HTTP 404 → ApiError → Result."""
        def _handler(req):
            return httpx.Response(
                404,
                json={"status": "error", "message": "Код активации не найден", "code": "not_found"},
            )

        routes = {"POST /api/activation/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.activation_redeem(
                ActivationRedeemInput(token="ACT_x", recipient_user_id=1, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "not_found"

    @pytest.mark.asyncio
    async def test_already_used_returns_result(self, client_factory):
        """already_used приходит с HTTP 409 → ApiError → Result."""
        def _handler(req):
            return httpx.Response(
                409,
                json={"status": "error", "message": "Код уже был использован", "code": "already_used"},
            )

        routes = {"POST /api/activation/redeem": _handler}
        async with client_factory(routes) as client:
            result = await client.activation_redeem(
                ActivationRedeemInput(token="ACT_x", recipient_user_id=1, bot_id=1)
            )
            assert result.success is False
            assert result.error_code == "already_used"
