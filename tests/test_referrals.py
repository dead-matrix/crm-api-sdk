"""Tests for ReferralsAPI."""
from __future__ import annotations

import pytest
import httpx

from crm_api.exceptions import ConfigError
from conftest import success_response


class TestReferralsAPI:
    @pytest.mark.asyncio
    async def test_referrals_info_success(self, client_factory):
        """Test referrals_info returns ReferralsInfoResult."""
        mock_data = {
            "ref_link": "https://t.me/bot?start=ref_abc123",
            "percent": 10,
            "registrations": 5,
            "ref_payments": 3,
            "ref_total_sum": 297000,
            "earned_usd": 30.0,
            "available_usd": 25.0,
            "referrees": [
                {
                    "user_id": 1001,
                    "full_name": "Referral One",
                    "username": "ref1",
                    "payments_count": 2,
                    "payments_sum_minor": 198000,
                    "payments": [
                        {
                            "date": "2024-01-15T10:00:00Z",
                            "amount_minor": 99000,
                            "commission_usd": 10.0,
                            "status": "paid",
                        },
                        {
                            "date": "2024-02-15T10:00:00Z",
                            "amount_minor": 99000,
                            "commission_usd": 10.0,
                            "status": "paid",
                        },
                    ],
                },
                {
                    "user_id": 1002,
                    "full_name": "Referral Two",
                    "username": None,
                    "payments_count": 1,
                    "payments_sum_minor": 99000,
                    "payments": [
                        {
                            "date": "2024-03-01T12:00:00Z",
                            "amount_minor": 99000,
                            "commission_usd": 10.0,
                            "status": "paid",
                        },
                    ],
                },
            ]
        }
        routes = {
            "GET /api/referrals/info": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.referrals_info(user_id=123)
            
            assert result.ref_link == "https://t.me/bot?start=ref_abc123"
            assert result.percent == 10
            assert result.registrations == 5
            assert result.ref_payments == 3
            assert result.ref_total_sum == 297000
            assert result.earned_usd == 30.0
            assert result.available_usd == 25.0
            
            assert len(result.referrees) == 2
            
            r1 = result.referrees[0]
            assert r1.user_id == 1001
            assert r1.full_name == "Referral One"
            assert r1.username == "ref1"
            assert r1.payments_count == 2
            assert r1.payments_sum_minor == 198000
            assert len(r1.payments) == 2
            assert r1.payments[0].amount_minor == 99000
            assert r1.payments[0].commission_usd == 10.0
            assert r1.payments[0].status == "paid"
            
            r2 = result.referrees[1]
            assert r2.user_id == 1002
            assert r2.username is None

    @pytest.mark.asyncio
    async def test_referrals_info_no_referrees(self, client_factory):
        """Test referrals_info with no referrees."""
        mock_data = {
            "ref_link": "https://t.me/bot?start=ref_xyz",
            "percent": 10,
            "registrations": 0,
            "ref_payments": 0,
            "ref_total_sum": 0,
            "earned_usd": 0.0,
            "available_usd": 0.0,
            "referrees": []
        }
        routes = {
            "GET /api/referrals/info": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.referrals_info(user_id=123)
            
            assert result.registrations == 0
            assert result.referrees == []

    @pytest.mark.asyncio
    async def test_referrals_info_referree_no_payments(self, client_factory):
        """Test referrals_info with referree having no payments."""
        mock_data = {
            "ref_link": "https://t.me/bot?start=ref_test",
            "percent": 10,
            "registrations": 1,
            "ref_payments": 0,
            "ref_total_sum": 0,
            "earned_usd": 0.0,
            "available_usd": 0.0,
            "referrees": [
                {
                    "user_id": 2001,
                    "full_name": "New Referral",
                    "username": "newref",
                    "payments_count": 0,
                    "payments_sum_minor": 0,
                    "payments": [],
                },
            ]
        }
        routes = {
            "GET /api/referrals/info": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.referrals_info(user_id=123)

            assert len(result.referrees) == 1
            assert result.referrees[0].payments_count == 0
            assert result.referrees[0].payments == []

    # --------------- Withdrawals ---------------

    @pytest.mark.asyncio
    async def test_withdraw_request_created(self, client_factory):
        routes = {
            "POST /api/referrals/withdraw/request": lambda req: success_response(
                {"status": "created", "withdrawal_id": 7, "amount_usd": 12.5, "method": "wallet"}
            ),
        }
        async with client_factory(routes) as client:
            res = await client.referrals_withdraw_request(user_id=123, method="wallet")
            assert res.status == "created"
            assert res.withdrawal_id == 7
            assert res.amount_usd == 12.5
            assert res.method == "wallet"
            assert res.available_usd is None

    @pytest.mark.asyncio
    async def test_withdraw_request_already_pending(self, client_factory):
        routes = {
            "POST /api/referrals/withdraw/request": lambda req: success_response(
                {"status": "already_pending", "withdrawal_id": 9, "amount_usd": 30.0}
            ),
        }
        async with client_factory(routes) as client:
            res = await client.referrals_withdraw_request(user_id=123, method="subscription")
            assert res.status == "already_pending"
            assert res.withdrawal_id == 9

    @pytest.mark.asyncio
    async def test_withdraw_request_no_balance(self, client_factory):
        routes = {
            "POST /api/referrals/withdraw/request": lambda req: success_response(
                {"status": "no_balance", "available_usd": 0.0}
            ),
        }
        async with client_factory(routes) as client:
            res = await client.referrals_withdraw_request(user_id=123, method="wallet")
            assert res.status == "no_balance"
            assert res.available_usd == 0.0
            assert res.withdrawal_id is None

    @pytest.mark.asyncio
    async def test_withdraw_request_bad_method_raises(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.referrals_withdraw_request(user_id=123, method="bank")

    @pytest.mark.asyncio
    async def test_withdraw_settle_partial(self, client_factory):
        captured = {}

        def _handler(req: httpx.Request):
            import json
            captured.update(json.loads(req.content))
            return success_response(
                {"status": "settled", "withdrawal_id": 7, "paid_usd": 30.0,
                 "available_after_usd": 30.0, "method": "subscription"}
            )

        routes = {"POST /api/referrals/withdraw/settle": _handler}
        async with client_factory(routes) as client:
            res = await client.referrals_withdraw_settle(
                user_id=123, amount_minor=3000, method="subscription", withdrawal_id=7
            )
            assert res.status == "settled"
            assert res.paid_usd == 30.0
            assert res.available_after_usd == 30.0
            assert res.method == "subscription"
            # withdrawal_id передан в теле
            assert captured["amount_minor"] == 3000
            assert captured["withdrawal_id"] == 7

    @pytest.mark.asyncio
    async def test_withdraw_settle_omits_withdrawal_id_when_none(self, client_factory):
        captured = {}

        def _handler(req: httpx.Request):
            import json
            captured.update(json.loads(req.content))
            return success_response(
                {"status": "settled", "withdrawal_id": 1, "paid_usd": 10.0,
                 "available_after_usd": 5.0, "method": "wallet"}
            )

        routes = {"POST /api/referrals/withdraw/settle": _handler}
        async with client_factory(routes) as client:
            await client.referrals_withdraw_settle(user_id=123, amount_minor=1000, method="wallet")
            assert "withdrawal_id" not in captured

    @pytest.mark.asyncio
    async def test_withdraw_settle_bad_amount_raises(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.referrals_withdraw_settle(user_id=123, amount_minor=0, method="wallet")

