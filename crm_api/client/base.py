from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, List, Tuple

import httpx
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from ..exceptions import (
    ApiError,
    AuthError,
    ConfigError,
    HttpError,
    ValidationError,
)
from ..utils import TokenCache, CachedJWT, parse_dt, parse_content_disposition

logger = logging.getLogger("crm_sdk")


class BaseCRMClient:
    """
    Базовый асинхронный клиент: инициализация, контекст-менеджер,
    аутентификация (JWT) и низкоуровневые HTTP-хелперы.
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

        self._retry = AsyncRetrying(
            wait=wait_exponential_jitter(initial=0.2, max=retry_max_jitter),
            stop=stop_after_attempt(max(1, request_retries)),
            retry=retry_if_exception_type(
                (
                    httpx.TransportError,
                    httpx.ReadTimeout,
                    httpx.RemoteProtocolError,
                )
            ),
            reraise=True,
        )

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
        body = None

        logger.debug("Issuing JWT for staff_id=%s", self._staff_id)

        try:
            async for attempt in self._retry:
                with attempt:
                    resp = await self._client.post(url, headers=headers, json=body)
                    data = await self._handle_response(resp, expect_success=True)
                    token = data.get("token")
                    expires_at = parse_dt(data.get("expires_at"))
                    if not token or not expires_at:
                        raise ApiError("Invalid auth response: missing token/expiry")
                    logger.debug("JWT issued for staff_id=%s exp=%s", self._staff_id, expires_at)
                    return token, expires_at
        except RetryError as re:
            raise HttpError(f"Auth request exhausted retries: {re}") from re

    # --------------- HTTP helpers ---------------

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]],
        need_auth: bool,
    ) -> Dict[str, Any] | List[Any] | Any:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        query = params or {}
        if need_auth:
            token = await self._ensure_jwt()
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Staff-ID"] = str(self._staff_id)

        try:
            async for attempt in self._retry:
                with attempt:
                    resp = await self._client.get(url, headers=headers, params=query)
                    if resp.status_code == 401 and need_auth:
                        logger.debug("401 received on GET, refreshing JWT and retrying once")
                        token = await self._refresh_jwt()
                        headers["Authorization"] = f"Bearer {token}"
                        resp = await self._client.get(url, headers=headers, params=query)
                    data = await self._handle_response(resp, expect_success=True)
                    return data
        except RetryError as re:
            raise HttpError(f"GET {path} exhausted retries: {re}") from re

    async def _post(
        self,
        path: str,
        json_body: Dict[str, Any] | None,
        *,
        need_auth: bool,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        query = params or {}
        if need_auth:
            token = await self._ensure_jwt()
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Staff-ID"] = str(self._staff_id)

        try:
            async for attempt in self._retry:
                with attempt:
                    resp = await self._client.post(url, headers=headers, params=query, json=json_body)
                    if resp.status_code == 401 and need_auth:
                        logger.debug("401 received, refreshing JWT and retrying once")
                        token = await self._refresh_jwt()
                        headers["Authorization"] = f"Bearer {token}"
                        resp = await self._client.post(url, headers=headers, params=query, json=json_body)
                    data = await self._handle_response(resp, expect_success=True)
                    return data
        except RetryError as re:
            raise HttpError(f"POST {path} exhausted retries: {re}") from re

    async def _put(
        self,
        path: str,
        json_body: Dict[str, Any] | None,
        *,
        need_auth: bool,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        query = params or {}
        if need_auth:
            token = await self._ensure_jwt()
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Staff-ID"] = str(self._staff_id)

        try:
            async for attempt in self._retry:
                with attempt:
                    resp = await self._client.put(url, headers=headers, params=query, json=json_body)
                    if resp.status_code == 401 and need_auth:
                        logger.debug("401 received on PUT, refreshing JWT and retrying once")
                        token = await self._refresh_jwt()
                        headers["Authorization"] = f"Bearer {token}"
                        resp = await self._client.put(url, headers=headers, params=query, json=json_body)
                    data = await self._handle_response(resp, expect_success=True)
                    return data
        except RetryError as re:
            raise HttpError(f"PUT {path} exhausted retries: {re}") from re

    async def _delete(
        self,
        path: str,
        *,
        need_auth: bool,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any] | List[Any] | Any:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        query = params or {}
        if need_auth:
            token = await self._ensure_jwt()
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Staff-ID"] = str(self._staff_id)

        try:
            async for attempt in self._retry:
                with attempt:
                    resp = await self._client.delete(url, headers=headers, params=query)
                    if resp.status_code == 401 and need_auth:
                        logger.debug("401 received on DELETE, refreshing JWT and retrying once")
                        token = await self._refresh_jwt()
                        headers["Authorization"] = f"Bearer {token}"
                        resp = await self._client.delete(url, headers=headers, params=query)
                    data = await self._handle_response(resp, expect_success=True)
                    return data
        except RetryError as re:
            raise HttpError(f"DELETE {path} exhausted retries: {re}") from re

    async def _get_file(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]],
        need_auth: bool,
    ) -> Tuple[bytes, Dict[str, str]]:
        url = f"{self._base_url}{path}"
        headers: Dict[str, str] = {}
        query = params or {}
        if need_auth:
            token = await self._ensure_jwt()
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Staff-ID"] = str(self._staff_id)

        try:
            async for attempt in self._retry:
                with attempt:
                    resp = await self._client.get(url, headers=headers, params=query)
                    if resp.status_code == 401 and need_auth:
                        logger.debug("401 received on GET(file), refreshing JWT and retrying once")
                        token = await self._refresh_jwt()
                        headers["Authorization"] = f"Bearer {token}"
                        resp = await self._client.get(url, headers=headers, params=query)

                    if resp.status_code == 200:
                        content = await resp.aread()
                        hdrs = {k.lower(): v for k, v in resp.headers.items()}
                        return content, hdrs

                    _ = await self._handle_response(resp, expect_success=True)
                    raise HttpError(
                        f"Unexpected non-200 without error envelope: {resp.status_code}",
                        status=resp.status_code,
                    )
        except RetryError as re:
            raise HttpError(f"GET(file) {path} exhausted retries: {re}") from re

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
            raise AuthError(f"{message} (code={code})")

        if status in (400, 422) or (isinstance(code, str) and code.upper() == "VALIDATION_ERROR"):
            raise ValidationError(message)

        raise ApiError(message, code=code, status=status)

