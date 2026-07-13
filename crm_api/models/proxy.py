from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ProxyCheckItem:
    proxy: str
    valid: bool
    ru_error: Optional[str]
    location: Optional[str]


@dataclass
class ProxyCheckResult:
    checked: int
    valid: int
    invalid: int
    results: List[ProxyCheckItem]


@dataclass
class ProxyItem:
    type: Optional[str]
    ip: Optional[str]
    port: Optional[int]
    login: Optional[str]
    password: Optional[str]
    valid: bool
    location: Optional[str]


@dataclass
class ProxyBindingsResult:
    """
    Сводка привязок прокси к аккаунтам пользователя (основной бот),
    GET /api/proxy/bindings. Аккаунт хранит прокси строкой; CRM матчит
    аккаунты с таблицей прокси по ip:port и считает агрегаты.
    """
    total_accounts: int
    accounts_with_proxy: int
    accounts_without_proxy: int
    total_proxies: int
    proxies_with_accounts: int
    proxies_without_accounts: int
    avg_accounts_per_proxy: float

