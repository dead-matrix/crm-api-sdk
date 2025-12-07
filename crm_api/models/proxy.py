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

