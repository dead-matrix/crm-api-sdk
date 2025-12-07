from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger("crm_sdk")


def parse_dt(value: str | None) -> Optional[datetime]:
    """Парсит ISO дату от API. Возвращает aware UTC или None."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            # считаем, что пришла UTC без TZ
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        logger.debug("Failed to parse datetime: %s", value)
        return None


def parse_content_disposition(value: str | None) -> Optional[str]:
    """
    Парсит Content-Disposition и возвращает имя файла, если есть.
    Пример: attachment; filename="log_123.txt"
    """
    if not value:
        return None
    try:
        # Простая и достаточно надежная выборка filename="..."
        m = re.search(r'filename\*=UTF-8\'\'([^;]+)', value)
        if m:
            return m.group(1)
        m = re.search(r'filename="([^"]+)"', value)
        if m:
            return m.group(1)
        m = re.search(r'filename=([^;]+)', value)
        if m:
            return m.group(1).strip()
    except Exception:
        return None
    return None


@dataclass
class CachedJWT:
    token: str
    expires_at: datetime  # aware UTC

    def is_valid(self, skew_seconds: int = 30) -> bool:
        now = datetime.now(timezone.utc)
        return now + timedelta(seconds=skew_seconds) < self.expires_at


class TokenCache:
    """Потокобезопасный in-memory кэш JWT по ключу (base_url, staff_id)."""

    def __init__(self):
        self._data: Dict[Tuple[str, int], CachedJWT] = {}
        self._locks: Dict[Tuple[str, int], asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def get(self, key: Tuple[str, int]) -> Optional[CachedJWT]:
        return self._data.get(key)

    async def set(self, key: Tuple[str, int], token: CachedJWT) -> None:
        self._data[key] = token

    async def get_lock(self, key: Tuple[str, int]) -> asyncio.Lock:
        # ленивое создание lock на ключ
        lock = self._locks.get(key)
        if lock:
            return lock
        async with self._global_lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[key] = lock
            return lock
