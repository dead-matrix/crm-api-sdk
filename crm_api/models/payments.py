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
    status: str
    status_ru: str
    client_id: int
    client_email: Optional[str]
    referer_id: Optional[int]
    staff_id: Optional[int]
    amount_minor: int
    fx_rate_rub_usd: Optional[float]
    currency: str
    discount_percent: Optional[int]
    description: Optional[str]
    items: List[dict]
    provider: Optional[str]
    pay_link: Optional[str]
    date_create: Optional[datetime]
    date_invoiced: Optional[datetime]
    date_paid: Optional[datetime]
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

@dataclass
class InvoiceInfoResult:
    uuid: str
    status: str
    status_ru: str
    client_id: int
    client_email: Optional[str]
    referer_id: Optional[int]
    staff_id: Optional[int]
    amount_minor: int
    fx_rate_rub_usd: Optional[float]
    currency: str
    discount_percent: Optional[int]
    description: str
    items: List[dict]
    provider: str
    pay_link: Optional[str]
    date_create: Optional[datetime]
    date_invoiced: Optional[datetime]
    date_paid: Optional[datetime]

