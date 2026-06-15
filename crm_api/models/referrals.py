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


@dataclass
class WithdrawRequestResult:
    """
    Результат заявки на вывод (POST /referrals/withdraw/request).

    status:
      - 'no_balance'       — выводить нечего (available_usd == 0);
      - 'already_pending'  — заявка уже открыта (бот показывает алерт);
      - 'created'          — создана заявка + outbox-событие в мессенджер.
    Поля заполняются по ветке: amount_usd/withdrawal_id — для pending/created,
    available_usd — для no_balance.
    """
    status: str
    withdrawal_id: Optional[int] = None
    amount_usd: Optional[float] = None
    method: Optional[str] = None
    available_usd: Optional[float] = None


@dataclass
class WithdrawSettleResult:
    """Результат проведения вывода (POST /referrals/withdraw/settle)."""
    status: str  # 'settled'
    withdrawal_id: int
    paid_usd: float
    available_after_usd: float
    method: str

