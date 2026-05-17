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
    pay_url: Optional[str]
    date_create: Optional[datetime]
    date_invoiced: Optional[datetime]
    date_paid: Optional[datetime]
    activation: List[ActivationLink]
    # Способ оплаты внутри провайдера ("sbp" | "crypto" для platega; None
    # для исторических записей и других провайдеров). Опционально: старые
    # версии CRM-API поле не возвращают.
    payment_method: Optional[str] = None


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
class PaymentsListResult:
    """
    Результат GET /api/payments?user_id=&limit=&offset=

    Сортировка: по date_create DESC (новые сверху). Поле count — количество
    элементов в текущей странице, не общий total.
    """
    limit: int
    offset: int
    count: int
    items: List[PaymentHistoryItem]


@dataclass
class Sale:
    """
    Элемент списка GET /api/payments/sales — оплаченный платёж за месяц.

    `category`: "main" | "extra" | "other" — определяется по category_key
    продуктов в позициях. "other"/неизвестные — мессенджер обычно игнорирует.

    `repeat_purchase`: True если у клиента уже была оплата в этой же категории
    раньше.
    """
    uuid: str
    user_id: int
    staff_id: Optional[int]
    amount_minor: int
    category: str
    repeat_purchase: bool
    date_paid: Optional[datetime]


@dataclass
class MonthlySalesResult:
    """
    Результат GET /api/payments/sales — все оплаченные платежи за текущий
    календарный месяц без фильтров.
    """
    month_start: Optional[datetime]
    payments: List[Sale]


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
    pay_url: Optional[str]
    date_create: Optional[datetime]
    date_invoiced: Optional[datetime]
    date_paid: Optional[datetime]
    # Способ оплаты внутри провайдера ("sbp" | "crypto" для platega; None
    # для исторических записей и других провайдеров). Опционально: старые
    # версии CRM-API поле не возвращают.
    payment_method: Optional[str] = None

