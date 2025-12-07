from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ReferreePayment:
    date: Optional[datetime]
    amount_minor: int
    commission_usd: float
    status: str


@dataclass
class ReferreeInfo:
    user_id: int
    full_name: Optional[str]
    username: Optional[str]
    payments_count: int
    payments_sum_minor: int
    payments: List[ReferreePayment]


@dataclass
class ReferralsInfoResult:
    ref_link: str
    percent: int
    registrations: int
    ref_payments: int
    ref_total_sum: int
    earned_usd: float
    available_usd: float
    referrees: List[ReferreeInfo]

