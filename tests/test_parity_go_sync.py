"""
Тесты функционала, портированного из Go SDK (синхронизация июнь 2026):

- accounts_list: include_removed + поля first_load/removed/proxy
- proxy_bindings
- servers_status
- reply-templates: поле command + reply_templates_set_command
- referrals_info: withdrawn_wallet_usd / withdrawn_subscription_usd
- payments: Sale.first_ever_purchase, provider_invoice_id, last_purchase_dates
- заморозка подписки: freeze_access/unfreeze_access, Dialog.frozen,
  UserBotInfo.frozen/frozen_at/frozen_expiry
"""
from __future__ import annotations

import json

import httpx
import pytest

from conftest import success_response

from crm_api import FreezeAccessInput
from crm_api.exceptions import ConfigError


# ───────────────────────── accounts ─────────────────────────


def _account_row(**overrides):
    row = {
        "session_name": "acc1",
        "valid": True,
        "spam_block": False,
        "is_connected": True,
        "location": "NL",
        "full_name": "Test",
        "username": "test",
        "phone": "+3100000",
        "premium": False,
        "commented": {"day": 1, "total": 2},
        "invited": {"day": 0, "total": 0},
        "stories": {"day": 0, "total": 0},
        "tagged": {"day": 0, "total": 0},
        "views": {"day": 0, "total": 0},
        "reactions": {"day": 0, "total": 0},
    }
    row.update(overrides)
    return row


class TestAccountsParity:
    @pytest.mark.asyncio
    async def test_accounts_list_new_fields(self, client_factory):
        rows = [
            _account_row(
                first_load="2026-05-01T12:30:00",
                removed=True,
                proxy="1.2.3.4:8080",
            )
        ]

        def check(req: httpx.Request) -> httpx.Response:
            assert req.url.params.get("include_removed") == "true"
            return success_response(rows)

        routes = {"GET /api/accounts/list": check}
        async with client_factory(routes) as client:
            items = await client.accounts_list(user_id=1, include_removed=True)
            assert items[0].removed is True
            assert items[0].proxy == "1.2.3.4:8080"
            assert items[0].first_load is not None
            assert items[0].first_load.year == 2026

    @pytest.mark.asyncio
    async def test_accounts_list_default_no_include_removed(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            assert "include_removed" not in req.url.params
            return success_response([_account_row()])

        routes = {"GET /api/accounts/list": check}
        async with client_factory(routes) as client:
            items = await client.accounts_list(user_id=1)
            assert items[0].removed is False
            assert items[0].proxy is None
            assert items[0].first_load is None


# ───────────────────────── proxy bindings ─────────────────────────


class TestProxyBindings:
    @pytest.mark.asyncio
    async def test_proxy_bindings(self, client_factory):
        data = {
            "total_accounts": 10,
            "accounts_with_proxy": 7,
            "accounts_without_proxy": 3,
            "total_proxies": 5,
            "proxies_with_accounts": 4,
            "proxies_without_accounts": 1,
            "avg_accounts_per_proxy": 1.75,
        }

        def check(req: httpx.Request) -> httpx.Response:
            assert req.url.params.get("user_id") == "42"
            return success_response(data)

        routes = {"GET /api/proxy/bindings": check}
        async with client_factory(routes) as client:
            res = await client.proxy_bindings(user_id=42)
            assert res.total_accounts == 10
            assert res.accounts_with_proxy == 7
            assert res.accounts_without_proxy == 3
            assert res.total_proxies == 5
            assert res.proxies_with_accounts == 4
            assert res.proxies_without_accounts == 1
            assert res.avg_accounts_per_proxy == 1.75

    @pytest.mark.asyncio
    async def test_proxy_bindings_invalid_user_id(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.proxy_bindings(user_id=0)


# ───────────────────────── servers status ─────────────────────────


class TestServersStatus:
    @pytest.mark.asyncio
    async def test_servers_status(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            assert req.url.params.get("user_id") == "123"
            assert req.url.params.get("bot_id") == "1"
            return success_response({"bound": True, "up": False})

        routes = {"GET /api/servers/status": check}
        async with client_factory(routes) as client:
            res = await client.servers_status(user_id=123)
            assert res.bound is True
            assert res.up is False

    @pytest.mark.asyncio
    async def test_servers_status_validation(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.servers_status(user_id=0)
            with pytest.raises(ConfigError):
                await client.servers_status(user_id=1, bot_id=0)


# ───────────────────────── reply templates command ─────────────────────────


def _template_payload(command=None):
    return {
        "id": 5,
        "publicId": "0197b1c8-0000-7000-8000-000000000001",
        "title": "Greeting",
        "kind": "single",
        "command": command,
        "creator": {"employeeId": 1, "name": "TraffSoft"},
        "items": [
            {"position": 0, "type": "text", "id": 11, "caption": "hello"},
        ],
        "createdAt": "2026-06-20T10:00:00+00:00",
        "updatedAt": "2026-06-20T10:00:00+00:00",
    }


class TestReplyTemplateCommand:
    @pytest.mark.asyncio
    async def test_list_and_get_map_command(self, client_factory):
        list_row = {
            "id": 5,
            "publicId": "0197b1c8-0000-7000-8000-000000000001",
            "title": "Greeting",
            "kind": "single",
            "command": "hi",
            "creator": {"employeeId": 1, "name": "TraffSoft"},
            "preview": {"firstItemType": "text", "captionExcerpt": "hello", "itemsCount": 1},
            "usageCount": 3,
        }
        routes = {
            "GET /api/reply-templates": lambda req: success_response([list_row]),
            "GET /api/reply-templates/{id}": lambda req: success_response(
                _template_payload(command="hi")
            ),
        }
        async with client_factory(routes) as client:
            items = await client.reply_templates_list()
            assert items[0].command == "hi"
            full = await client.reply_templates_get(5)
            assert full.command == "hi"

    @pytest.mark.asyncio
    async def test_set_command_normalizes(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content)
            assert body == {"command": "hi_there"}
            return success_response(_template_payload(command="hi_there"))

        routes = {"PATCH /api/reply-templates/{id}": check}
        async with client_factory(routes) as client:
            # trim + срез "/" + lower-case
            full = await client.reply_templates_set_command(5, "  /Hi_There  ")
            assert full.command == "hi_there"

    @pytest.mark.asyncio
    async def test_set_command_clear(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content)
            assert body == {"command": None}
            return success_response(_template_payload(command=None))

        routes = {"PATCH /api/reply-templates/{id}": check}
        async with client_factory(routes) as client:
            for value in (None, "", "  ", "/", " / "):
                full = await client.reply_templates_set_command(5, value)
                assert full.command is None

    @pytest.mark.asyncio
    async def test_set_command_validation(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_set_command(0, "hi")
            with pytest.raises(ConfigError):
                await client.reply_templates_set_command(5, "has space")
            with pytest.raises(ConfigError):
                await client.reply_templates_set_command(5, "bad-dash")
            with pytest.raises(ConfigError):
                await client.reply_templates_set_command(5, "x" * 65)

    @pytest.mark.asyncio
    async def test_set_command_cyrillic_ok(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content)
            assert body == {"command": "привет"}
            return success_response(_template_payload(command="привет"))

        routes = {"PATCH /api/reply-templates/{id}": check}
        async with client_factory(routes) as client:
            full = await client.reply_templates_set_command(5, "/Привет")
            assert full.command == "привет"


# ───────────────────────── referrals withdrawn breakdown ─────────────────────────


class TestReferralsWithdrawnBreakdown:
    @pytest.mark.asyncio
    async def test_referrals_info_withdrawn_fields(self, client_factory):
        data = {
            "ref_link": "https://t.me/bot?start=r_1",
            "percent": 20,
            "registrations": 3,
            "ref_payments": 2,
            "ref_total_sum": 10000,
            "earned_usd": 25.5,
            "available_usd": 4.5,
            "withdrawn_wallet_usd": 20.0,
            "withdrawn_subscription_usd": 5.5,
            "referrees": [],
        }
        routes = {"GET /api/referrals/info": lambda req: success_response(data)}
        async with client_factory(routes) as client:
            res = await client.referrals_info(user_id=1)
            assert res.withdrawn_wallet_usd == 20.0
            assert res.withdrawn_subscription_usd == 5.5

    @pytest.mark.asyncio
    async def test_referrals_info_withdrawn_fields_absent(self, client_factory):
        """Старый CRM-API без разбивки — поля дефолтятся в 0.0."""
        data = {
            "ref_link": "https://t.me/bot?start=r_1",
            "percent": 20,
            "registrations": 0,
            "ref_payments": 0,
            "ref_total_sum": 0,
            "earned_usd": 0.0,
            "available_usd": 0.0,
            "referrees": [],
        }
        routes = {"GET /api/referrals/info": lambda req: success_response(data)}
        async with client_factory(routes) as client:
            res = await client.referrals_info(user_id=1)
            assert res.withdrawn_wallet_usd == 0.0
            assert res.withdrawn_subscription_usd == 0.0


# ───────────────────────── payments ─────────────────────────


class TestPaymentsParity:
    @pytest.mark.asyncio
    async def test_sales_first_ever_purchase(self, client_factory):
        data = {
            "month_start": "2026-06-01T00:00:00+00:00",
            "payments": [
                {
                    "uuid": "u1",
                    "user_id": 1,
                    "staff_id": None,
                    "amount_minor": 100,
                    "category": "main",
                    "repeat_purchase": False,
                    "first_ever_purchase": True,
                    "date_paid": "2026-06-02T10:00:00+00:00",
                },
                {
                    "uuid": "u2",
                    "user_id": 2,
                    "staff_id": 3,
                    "amount_minor": 200,
                    "category": "extra",
                    "repeat_purchase": True,
                    # поле отсутствует у старых CRM-API → False
                },
            ],
        }
        routes = {"GET /api/payments/sales": lambda req: success_response(data)}
        async with client_factory(routes) as client:
            res = await client.get_monthly_sales()
            assert res.payments[0].first_ever_purchase is True
            assert res.payments[1].first_ever_purchase is False

    @pytest.mark.asyncio
    async def test_get_payments_provider_invoice_id(self, client_factory):
        data = {
            "limit": 10,
            "offset": 0,
            "count": 1,
            "items": [
                {
                    "uuid": "u1",
                    "status": "paid",
                    "status_ru": "Оплачен",
                    "client_id": 1,
                    "amount_minor": 100,
                    "currency": "RUB",
                    "items": [],
                    "provider": "platega",
                    "provider_invoice_id": "txn-123",
                    "activation": [],
                }
            ],
        }
        routes = {"GET /api/payments": lambda req: success_response(data)}
        async with client_factory(routes) as client:
            res = await client.get_payments(limit=10)
            assert res.items[0].provider_invoice_id == "txn-123"

    @pytest.mark.asyncio
    async def test_last_purchase_dates(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content)
            assert body == {"user_ids": [1, 2, 3]}
            # id=3 отсутствует в ответе — защитная ветка должна дозаполнить None
            return success_response({"1": "2026-06-15T10:00:00+00:00", "2": None})

        routes = {"POST /api/payments/last-purchase": check}
        async with client_factory(routes) as client:
            res = await client.last_purchase_dates([1, 2, 3])
            assert set(res.keys()) == {1, 2, 3}
            assert res[1] is not None and res[1].day == 15
            assert res[2] is None
            assert res[3] is None

    @pytest.mark.asyncio
    async def test_last_purchase_dates_empty_input(self, client_factory):
        # Пустой список не должен ходить в сеть.
        async with client_factory({}) as client:
            res = await client.last_purchase_dates([])
            assert res == {}


# ───────────────────────── subscription freeze ─────────────────────────


class TestFreezeAccess:
    @pytest.mark.asyncio
    async def test_freeze_access(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content)
            assert body == {"user_id": 1, "idempotency_key": "k1"}
            return success_response(
                {"user_id": 1, "frozen": True, "bots": {"1": {"frozen": True}}}
            )

        routes = {"POST /api/access/freeze": check}
        async with client_factory(routes) as client:
            res = await client.freeze_access(
                FreezeAccessInput(user_id=1, idempotency_key="k1")
            )
            assert res.user_id == 1
            assert res.changed is True
            assert res.bots == {"1": {"frozen": True}}

    @pytest.mark.asyncio
    async def test_unfreeze_access_with_bot_id(self, client_factory):
        def check(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content)
            assert body == {"user_id": 1, "bot_id": 3}
            return httpx.Response(
                200,
                json={
                    "status": "success",
                    "data": {"user_id": 1, "unfrozen": False, "bots": {}},
                },
            )

        routes = {"POST /api/access/unfreeze": check}
        async with client_factory(routes) as client:
            res = await client.unfreeze_access(FreezeAccessInput(user_id=1, bot_id=3))
            assert res.changed is False
            assert res.bots == {}

    @pytest.mark.asyncio
    async def test_dialogs_frozen_field(self, client_factory):
        data = {
            "dialogs": [
                {
                    "user_id": 1,
                    "full_name": "A",
                    "has_active_subscription": True,
                    "frozen": True,
                    "status": None,
                    "status_color": None,
                },
                {
                    "user_id": 2,
                    "full_name": "B",
                    "has_active_subscription": False,
                },
            ]
        }
        routes = {
            "GET /api/dialogs/sales": lambda req: success_response(data),
            "GET /api/dialogs/sales/search": lambda req: success_response(
                {"dialogs": data["dialogs"], "limit": 50, "offset": 0}
            ),
        }
        async with client_factory(routes) as client:
            dialogs = await client.get_dialogs("sales")
            assert dialogs[0].frozen is True
            assert dialogs[1].frozen is False
            found = await client.search_dialogs("sales", "A")
            assert found.dialogs[0].frozen is True
            assert found.dialogs[1].frozen is False

    @pytest.mark.asyncio
    async def test_get_user_frozen_fields(self, client_factory):
        data = {
            "user_id": 1,
            "full_name": "A",
            "username": "a",
            "status": None,
            "bots_info": [
                {
                    "bot_id": 1,
                    "bot_name": "Main",
                    "registered": "2026-01-01T00:00:00",
                    "refer": None,
                    "access": ["chatgpt"],
                    "access_end": None,
                    "frozen": True,
                    "frozen_at": "2026-06-25T12:00:00",
                    "frozen_expiry": {"chatgpt": "2026-07-10T12:00:00"},
                },
                {
                    "bot_id": 3,
                    "bot_name": "Poster",
                    "registered": None,
                    "refer": None,
                    "access": None,
                    "access_end": None,
                    # полей заморозки нет (старый CRM-API) → дефолты
                },
            ],
        }
        routes = {"GET /api/users/{id}": lambda req: success_response(data)}
        async with client_factory(routes) as client:
            res = await client.get_user(1)
            b1, b3 = res.bots_info
            assert b1.frozen is True
            assert b1.frozen_at is not None and b1.frozen_at.day == 25
            assert b1.frozen_expiry == {"chatgpt": "2026-07-10T12:00:00"}
            assert b3.frozen is False
            assert b3.frozen_at is None
            assert b3.frozen_expiry is None
