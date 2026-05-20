from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional, List, Set, Tuple

import httpx

from ..exceptions import (
    ApiError,
    AuthError,
    ConfigError,
    HttpError,
    ValidationError,
)
from ..utils import TokenCache, CachedJWT, parse_dt, parse_content_disposition

logger = logging.getLogger("crm_sdk")

DEFAULT_RETRY_STATUS_CODES: frozenset[int] = frozenset({429, 502, 503, 504})
IDEMPOTENT_METHODS: frozenset[str] = frozenset(
    {"GET", "HEAD", "OPTIONS", "TRACE", "PUT", "DELETE"}
)

_RETRYABLE_TRANSPORT_EXC = (
    httpx.TransportError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)


class BaseCRMClient:
    """
    Базовый асинхронный клиент: инициализация, контекст-менеджер,
    аутентификация (JWT) и низкоуровневые HTTP-хелперы.

    Retry-поведение (паритет с Go SDK):
    - Транспортные ошибки (`httpx.TransportError` и подкласс) ретраятся
      для любых методов.
    - Статус-коды из `retry_status_codes` (по умолчанию 429/502/503/504)
      ретраятся только для идемпотентных методов (GET/HEAD/OPTIONS/TRACE/PUT/DELETE),
      если не передан `retry_non_idempotent=True`.
    - Между попытками используется экспоненциальный backoff с jitter.
    """

    _token_cache = TokenCache()

    def __init__(
        self,
        base_url: str,
        staff_id: int,
        *,
        timeout: float = 10.0,
        request_retries: int = 3,
        retry_max_jitter: float = 1.0,
        retry_base_delay: float = 0.2,
        retry_max_delay: float = 1.0,
        retry_status_codes: Optional[Iterable[int]] = None,
        retry_non_idempotent: bool = False,
        service_token: Optional[str] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        if staff_id <= 0:
            raise ConfigError("staff_id must be positive integer")

        if not service_token or not str(service_token).strip():
            raise ConfigError("service_token must be provided")
        self._service_token = str(service_token).strip()
        self._base_url = base_url.rstrip("/")
        self._staff_id = staff_id

        self._timeout = httpx.Timeout(timeout)
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            headers={"Content-Type": "application/json"},
            transport=transport,
        )

        self._request_retries = max(1, int(request_retries))
        self._retry_base_delay = max(0.0, float(retry_base_delay))
        # Совместимость с прежним API: retry_max_jitter использовался для
        # верхней границы экспоненциального ожидания. Сохраняем поведение,
        # уважая больший из (retry_max_jitter, retry_max_delay).
        self._retry_max_delay = max(self._retry_base_delay, float(retry_max_delay), float(retry_max_jitter))
        self._retry_status_codes: Set[int] = set(
            retry_status_codes if retry_status_codes is not None else DEFAULT_RETRY_STATUS_CODES
        )
        self._retry_non_idempotent = bool(retry_non_idempotent)

    # --------------- Context manager ---------------

    async def __aenter__(self) -> "BaseCRMClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Закрыть HTTP клиент."""
        await self._client.aclose()

    # --------------- Auth helpers ---------------


    async def _ensure_jwt(self) -> str:
        key = (self._base_url, self._staff_id)
        cached = await self._token_cache.get(key)
        if cached and cached.is_valid():
            return cached.token

        lock = await self._token_cache.get_lock(key)
        async with lock:
            cached = await self._token_cache.get(key)
            if cached and cached.is_valid():
                return cached.token
            jwt_token, exp = await self._issue_jwt()
            await self._token_cache.set(key, CachedJWT(token=jwt_token, expires_at=exp))
            return jwt_token

    async def _refresh_jwt(self) -> str:
        key = (self._base_url, self._staff_id)
        lock = await self._token_cache.get_lock(key)
        async with lock:
            jwt_token, exp = await self._issue_jwt()
            await self._token_cache.set(key, CachedJWT(token=jwt_token, expires_at=exp))
            return jwt_token

    async def _issue_jwt(self) -> tuple[str, Any]:
        url = f"{self._base_url}/api/staff/{self._staff_id}/auth"
        headers = {"X-Service-Token": self._service_token}

        logger.debug("Issuing JWT for staff_id=%s", self._staff_id)

        # POST не идемпотентен, но эндпоинт авторизации повторяемый
        # (вытаскивает текущий токен из БД и подписывает заново). Принудительно
        # разрешаем retry-на-статус, чтобы не падать на временных 5xx инфры.
        resp = await self._do_with_retry(
            "POST",
            url,
            headers=headers,
            params=None,
            json_body=None,
            allow_status_retry=True,
        )
        data = await self._handle_response(resp, expect_success=True)
        token = data.get("token")
        expires_at = parse_dt(data.get("expires_at"))
        if not token or not expires_at:
            raise ApiError("Invalid auth response: missing token/expiry")
        logger.debug("JWT issued for staff_id=%s exp=%s", self._staff_id, expires_at)
        return token, expires_at

    # --------------- Core retry primitive ---------------

    def _backoff_delay(self, attempt: int) -> float:
        """Экспоненциальный backoff с jitter (паритет с Go SDK)."""
        base = self._retry_base_delay
        cap = self._retry_max_delay
        if base <= 0:
            return 0.0
        delay = base * (2 ** (attempt - 1))
        if delay > cap:
            delay = cap
        delay += random.uniform(0.0, base)
        if delay > cap:
            delay = cap
        return delay

    def _should_retry_status(self, method: str, status: int, allow_status_retry: bool) -> bool:
        if status not in self._retry_status_codes:
            return False
        if allow_status_retry or self._retry_non_idempotent:
            return True
        return method.upper() in IDEMPOTENT_METHODS

    async def _do_with_retry(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        json_body: Any = None,
        allow_status_retry: bool = False,
    ) -> httpx.Response:
        """
        Выполняет HTTP-запрос с ретраями.

        Возвращает сырой `httpx.Response`. Парсинг envelope/ошибок остаётся
        на вызывающем коде (`_handle_response`).
        """
        last_exc: Optional[Exception] = None
        attempts = self._request_retries

        for attempt in range(1, attempts + 1):
            try:
                resp = await self._client.request(
                    method,
                    url,
                    headers=headers,
                    params=params or {},
                    json=json_body,
                )
            except _RETRYABLE_TRANSPORT_EXC as e:
                last_exc = e
                if attempt == attempts:
                    raise HttpError(
                        f"{method} {url} exhausted retries: {type(e).__name__}: {e}"
                    ) from e
                delay = self._backoff_delay(attempt)
                logger.warning(
                    "transport retry %s %s attempt=%s/%s delay=%.3fs error=%s",
                    method, url, attempt, attempts, delay, e,
                )
                if delay > 0:
                    await asyncio.sleep(delay)
                continue

            if attempt < attempts and self._should_retry_status(method, resp.status_code, allow_status_retry):
                delay = self._backoff_delay(attempt)
                logger.warning(
                    "status retry %s %s attempt=%s/%s status=%s delay=%.3fs",
                    method, url, attempt, attempts, resp.status_code, delay,
                )
                # Освобождаем подключение перед повтором.
                await resp.aclose()
                if delay > 0:
                    await asyncio.sleep(delay)
                continue

            return resp

        # Защитная ветка: в норме сюда не доходим — последняя итерация либо
        # вернула resp, либо бросила исключение.
        if last_exc is not None:
            raise HttpError(f"{method} {url} exhausted retries") from last_exc
        raise HttpError(f"{method} {url} exhausted retries")

    # --------------- HTTP helpers ---------------

    def _auth_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "X-Staff-ID": str(self._staff_id),
        }

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]],
        json_body: Any,
        need_auth: bool,
    ) -> Dict[str, Any] | List[Any] | Any:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        if need_auth:
            token = await self._ensure_jwt()
            headers.update(self._auth_headers(token))

        resp = await self._do_with_retry(
            method, url, headers=headers, params=params, json_body=json_body,
        )

        if resp.status_code == 401 and need_auth:
            logger.debug("401 received on %s %s, refreshing JWT and retrying once", method, path)
            token = await self._refresh_jwt()
            headers.update(self._auth_headers(token))
            resp = await self._do_with_retry(
                method, url, headers=headers, params=params, json_body=json_body,
            )

        return await self._handle_response(resp, expect_success=True)

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]],
        need_auth: bool,
    ) -> Dict[str, Any] | List[Any] | Any:
        return await self._request_json("GET", path, params=params, json_body=None, need_auth=need_auth)

    async def _post(
        self,
        path: str,
        json_body: Dict[str, Any] | None,
        *,
        need_auth: bool,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self._request_json("POST", path, params=params, json_body=json_body, need_auth=need_auth)

    async def _put(
        self,
        path: str,
        json_body: Dict[str, Any] | None,
        *,
        need_auth: bool,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self._request_json("PUT", path, params=params, json_body=json_body, need_auth=need_auth)

    async def _delete(
        self,
        path: str,
        *,
        need_auth: bool,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any] | List[Any] | Any:
        return await self._request_json("DELETE", path, params=params, json_body=None, need_auth=need_auth)

    async def _get_file(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]],
        need_auth: bool,
    ) -> Tuple[bytes, Dict[str, str]]:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        if need_auth:
            token = await self._ensure_jwt()
            headers.update(self._auth_headers(token))

        resp = await self._do_with_retry(
            "GET", url, headers=headers, params=params, json_body=None,
        )

        if resp.status_code == 401 and need_auth:
            logger.debug("401 received on GET(file), refreshing JWT and retrying once")
            token = await self._refresh_jwt()
            headers.update(self._auth_headers(token))
            resp = await self._do_with_retry(
                "GET", url, headers=headers, params=params, json_body=None,
            )

        if resp.status_code == 200:
            content = await resp.aread()
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return content, hdrs

        _ = await self._handle_response(resp, expect_success=True)
        raise HttpError(
            f"Unexpected non-200 without error envelope: {resp.status_code}",
            status=resp.status_code,
        )

    async def _handle_response(
        self,
        resp: httpx.Response,
        *,
        expect_success: bool,
    ) -> Dict[str, Any] | List[Any] | Any:
        text = resp.text
        status = resp.status_code

        try:
            payload = resp.json()
        except json.JSONDecodeError as e:
            raise HttpError(f"Invalid JSON response (status={status}): {text[:200]}") from e

        api_status = payload.get("status")
        if api_status == "success":
            return payload.get("data")

        message = payload.get("message") or "API error"
        code = payload.get("code")

        if status in (401, 403):
            raise AuthError(message, code=code, status=status)

        if status in (400, 422) or (isinstance(code, str) and code.upper() == "VALIDATION_ERROR"):
            raise ValidationError(message, code=code, status=status)

        raise ApiError(message, code=code, status=status)
