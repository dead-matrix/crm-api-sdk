from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CalcItem:
    id: int
    title: str
    unit_price_minor: int
    discount_percent: int
    unit_price_discounted_minor: int
    quantity: int
    line_total_minor: int


@dataclass
class PaymentsCalculateResult:
    amount_minor: int
    amount_usd: Optional[float]
    currency: str
    items: List[CalcItem]


@dataclass
class InvoiceDraftResult:
    uuid: str
    pay_link: str
    status: str


@dataclass
class InvoiceIssueResult:
    pay_url: str
    status: str


@dataclass
class ActivationLink:
    bot_id: Optional[int]
    code: str
    is_used: bool
    url: str


@dataclass
class PaymentHistoryItem:
    uuid: str
    date_create: Optional[datetime]
    date_invoiced: Optional[datetime]
    date_paid: Optional[datetime]
    status: str
    amount_minor: int
    discount_percent: Optional[int]
    currency: str
    items: List[dict]
    client_email: Optional[str]
    pay_url: Optional[str]
    provider: Optional[str]
    activation: List[ActivationLink]


@dataclass
class ConfirmPaymentResult:
    uuid: str
    status: str


@dataclass
class RefundResult:
    uuid: str
    provider: str
    allowed: bool
    message: str
    status: Optional[str] = None

