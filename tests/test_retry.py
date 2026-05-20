"""
Тесты retry-поведения BaseCRMClient.

Паритет с Go SDK:
- транспортные ошибки ретраятся для любого метода;
- статусы из retry_status_codes (по умолчанию 429/502/503/504) ретраятся
  только для идемпотентных методов (GET/PUT/DELETE/...) — если не передан
  retry_non_idempotent=True;
- задержки между попытками с экспоненциальным backoff (в тестах
  retry_base_delay=0 → ноль задержки, чтобы тест не висел).
"""
from __future__ import annotations

import asyncio
from typing import List

import httpx
import pytest

from conftest import success_response

from crm_api.client import CRMApiClient
from crm_api.client.base import DEFAULT_RETRY_STATUS_CODES, IDEMPOTENT_METHODS
from crm_api.exceptions import ApiError, HttpError


def _client(transport: httpx.MockTransport, **overrides) -> CRMApiClient:
    kwargs = dict(
        base_url="https://test-crm.example",
        staff_id=1,
        service_token="test-service-token",
        transport=transport,
        request_retries=3,
        retry_base_delay=0.0,
        retry_max_delay=0.0,
    )
    kwargs.update(overrides)
    return CRMApiClient(**kwargs)


class TestRetryDefaults:
    def test_default_status_codes_match_python_go_contract(self):
        assert DEFAULT_RETRY_STATUS_CODES == frozenset({429, 502, 503, 504})

    def test_idempotent_methods(self):
        assert {"GET", "PUT", "DELETE"}.issubset(IDEMPOTENT_METHODS)
        assert "POST" not in IDEMPOTENT_METHODS
        assert "PATCH" not in IDEMPOTENT_METHODS


class TestRetryOnStatus:
    @pytest.mark.asyncio
    async def test_get_retries_on_503_then_success(self):
        calls: List[str] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            calls.append(req.method)
            if len(calls) < 3:
                return httpx.Response(503, text="upstream temporary")
            return success_response({"name": "ok", "role": "admin", "is_active": True, "access": {}})

        async with _client(httpx.MockTransport(handler)) as client:
            result = await client.get_staff()
            assert result.name == "ok"

        # POST для auth + 2 неудачных GET + 1 успешный GET
        assert calls == ["GET", "GET", "GET"]

    @pytest.mark.asyncio
    async def test_get_retries_on_429(self):
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            if len(attempts) < 2:
                return httpx.Response(429, text="rate limited")
            return success_response([])

        async with _client(httpx.MockTransport(handler)) as client:
            result = await client.list_departments()
            assert result == []

        assert len(attempts) == 2

    @pytest.mark.asyncio
    async def test_get_exhausts_retries_and_raises(self):
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            return httpx.Response(502, text="bad gateway")

        async with _client(httpx.MockTransport(handler)) as client:
            with pytest.raises((HttpError, ApiError)):
                await client.list_departments()

        # request_retries=3 → 3 попытки целевого запроса
        assert len(attempts) == 3

    @pytest.mark.asyncio
    async def test_post_not_retried_on_status_by_default(self):
        """POST не идемпотентен — по умолчанию ретрай на статус не делаем."""
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            return httpx.Response(503, json={"status": "error", "message": "down"})

        async with _client(httpx.MockTransport(handler)) as client:
            with pytest.raises((HttpError, ApiError)):
                await client.change_dialog_status(user_id=1, status_id=2)

        assert len(attempts) == 1, "POST must not be retried on 5xx by default"

    @pytest.mark.asyncio
    async def test_post_retried_when_retry_non_idempotent(self):
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            if len(attempts) < 2:
                return httpx.Response(503, text="temporary")
            return success_response({"status": "Новый"})

        async with _client(httpx.MockTransport(handler), retry_non_idempotent=True) as client:
            result = await client.change_dialog_status(user_id=1, status_id=2)
            assert result.status == "Новый"

        assert len(attempts) == 2

    @pytest.mark.asyncio
    async def test_500_not_retried_by_default(self):
        """500 не входит в дефолтный список retry-кодов (паритет с Go SDK)."""
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            return httpx.Response(500, json={"status": "error", "message": "boom"})

        async with _client(httpx.MockTransport(handler)) as client:
            with pytest.raises((HttpError, ApiError)):
                await client.list_departments()

        assert len(attempts) == 1


class TestRetryOnTransport:
    @pytest.mark.asyncio
    async def test_transport_error_is_retried_on_post(self):
        """Сетевые ошибки ретраятся даже для POST — это безопасно,
        потому что запрос мог не дойти до сервера."""
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            if len(attempts) == 1:
                raise httpx.ConnectError("connection refused")
            return success_response({"status": "Новый"})

        async with _client(httpx.MockTransport(handler)) as client:
            result = await client.change_dialog_status(user_id=1, status_id=2)
            assert result.status == "Новый"

        assert len(attempts) == 2

    @pytest.mark.asyncio
    async def test_transport_error_exhausts(self):
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            raise httpx.ConnectError("connection refused")

        async with _client(httpx.MockTransport(handler)) as client:
            with pytest.raises(HttpError):
                await client.list_departments()

        assert len(attempts) == 3


class TestRetryStatusOverride:
    @pytest.mark.asyncio
    async def test_custom_retry_status_codes(self):
        """Можно настроить список retry-кодов через конструктор."""
        attempts: List[int] = []

        def handler(req: httpx.Request) -> httpx.Response:
            if req.url.path == "/api/staff/1/auth":
                return httpx.Response(200, json={
                    "status": "success",
                    "data": {"token": "tkn", "expires_at": "2030-01-01T00:00:00+00:00"},
                })
            attempts.append(1)
            if len(attempts) < 2:
                return httpx.Response(418, text="teapot")
            return success_response([])

        async with _client(httpx.MockTransport(handler), retry_status_codes=[418]) as client:
            await client.list_departments()

        assert len(attempts) == 2
