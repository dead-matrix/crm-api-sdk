from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import ConfigError
from ..models import (
    PaymentsCalculateInput,
    PaymentsCalculateResult,
    CalcItem,
    InvoiceDraftInput,
    InvoiceDraftResult,
    InvoiceIssueInput,
    InvoiceIssueResult,
    PaymentHistoryItem,
    PaymentsListResult,
    ActivationLink,
    ConfirmPaymentResult,
    RefundInput,
    RefundResult,
    InvoiceInfoResult,
    Sale,
    MonthlySalesResult,
)
from ..utils import parse_dt


class PaymentsAPI:
    # --------------- Payments ---------------

    async def calculate_payment(self, data: PaymentsCalculateInput) -> PaymentsCalculateResult:
        d = await self._post("/api/payments/calculate", data.model_dump(), need_auth=True)
        items: List[CalcItem] = []
        for i in d.get("items") or []:
            items.append(
                CalcItem(
                    id=int(i["id"]),
                    title=str(i["title"]),
                    unit_price_minor=int(i["unit_price_minor"]),
                    discount_percent=int(i["discount_percent"]),
                    unit_price_discounted_minor=int(i["unit_price_discounted_minor"]),
                    quantity=int(i["quantity"]),
                    line_total_minor=int(i["line_total_minor"]),
                )
            )
        return PaymentsCalculateResult(
            amount_minor=int(d["amount_minor"]),
            amount_usd=d.get("amount_usd"),
            currency=str(d.get("currency", "RUB")),
            items=items,
        )

    async def create_invoice_draft(self, data: InvoiceDraftInput) -> InvoiceDraftResult:
        # exclude_none: не отправляем payment_method=null для провайдеров,
        # которые его не используют (yookassa/cryptocloud/heleket).
        d = await self._post("/api/payments/invoice/draft", data.model_dump(exclude_none=True), need_auth=True)
        return InvoiceDraftResult(uuid=str(d["uuid"]), pay_link=str(d["pay_link"]), status=str(d["status"]))

    async def issue_invoice(self, data: InvoiceIssueInput) -> InvoiceIssueResult:
        d = await self._post("/api/payments/invoice/issue", data.model_dump(), need_auth=True)
        return InvoiceIssueResult(pay_url=str(d["pay_url"]), status=str(d["status"]))

    async def get_invoice_info(self, uuid: str) -> InvoiceInfoResult:
        """
        Проверка существования и получение информации о платеже по UUID.
        Автоматически запрашивает актуальный статус у провайдера для выставленных платежей.
        """
        d = await self._get(f"/api/payments/invoice/{uuid}", params=None, need_auth=True)
        return InvoiceInfoResult(
            uuid=str(d["uuid"]),
            status=str(d["status"]),
            status_ru=str(d["status_ru"]),
            client_id=int(d["client_id"]),
            client_email=d.get("client_email"),
            referer_id=d.get("referer_id"),
            staff_id=d.get("staff_id"),
            amount_minor=int(d["amount_minor"]),
            fx_rate_rub_usd=d.get("fx_rate_rub_usd"),
            currency=str(d.get("currency", "RUB")),
            discount_percent=d.get("discount_percent"),
            description=str(d["description"]),
            items=d.get("items") or [],
            provider=str(d["provider"]),
            pay_link=d.get("pay_link"),
            pay_url=d.get("pay_url"),
            date_create=parse_dt(d.get("date_create")),
            date_invoiced=parse_dt(d.get("date_invoiced")),
            date_paid=parse_dt(d.get("date_paid")),
        )

    async def get_payments(
        self,
        user_id: Optional[int] = None,
        limit: int = 100_000,
        offset: int = 0,
    ) -> PaymentsListResult:
        """
        История платежей с пагинацией.

        Args:
            user_id: фильтр по покупателю; None → все платежи.
            limit: максимум записей в странице (>= 1, default 100_000).
            offset: смещение (>= 0, default 0).

        Сортировка на сервере — по date_create DESC (новые сверху).
        """
        if limit <= 0:
            raise ConfigError("limit must be positive integer")
        if offset < 0:
            raise ConfigError("offset must be non-negative integer")

        params: Dict[str, Any] = {"limit": int(limit), "offset": int(offset)}
        if user_id is not None:
            params["user_id"] = int(user_id)

        data = await self._get("/api/payments", params=params, need_auth=True)

        # Backward-compat: до пагинации CRM-API возвращал плоский массив
        # платежей вместо envelope. Если сервер ещё не обновлён — сами
        # обёртываем в формат новой схемы.
        if isinstance(data, list):
            envelope: Dict[str, Any] = {
                "limit": limit,
                "offset": offset,
                "count": len(data),
                "items": data,
            }
        else:
            envelope = data

        items: List[PaymentHistoryItem] = []
        for p in (envelope.get("items") or []):
            activation: List[ActivationLink] = []
            for ac in p.get("activation") or []:
                activation.append(
                    ActivationLink(
                        bot_id=ac.get("bot_id"),
                        code=str(ac.get("code")),
                        is_used=bool(ac.get("is_used")),
                        url=str(ac.get("url")),
                    )
                )
            items.append(
                PaymentHistoryItem(
                    uuid=str(p["uuid"]),
                    status=str(p.get("status")),
                    status_ru=str(p.get("status_ru", "")),
                    client_id=int(p.get("client_id", 0)),
                    client_email=p.get("client_email"),
                    referer_id=p.get("referer_id"),
                    staff_id=p.get("staff_id"),
                    amount_minor=int(p.get("amount_minor", 0)),
                    fx_rate_rub_usd=p.get("fx_rate_rub_usd"),
                    currency=str(p.get("currency", "RUB")),
                    discount_percent=p.get("discount_percent"),
                    description=p.get("description"),
                    items=p.get("items") or [],
                    provider=p.get("provider"),
                    pay_link=p.get("pay_link"),
                    pay_url=p.get("pay_url"),
                    date_create=parse_dt(p.get("date_create")),
                    date_invoiced=parse_dt(p.get("date_invoiced")),
                    date_paid=parse_dt(p.get("date_paid")),
                    activation=activation,
                )
            )
        return PaymentsListResult(
            limit=int(data.get("limit", limit)),
            offset=int(data.get("offset", offset)),
            count=int(data.get("count", len(items))),
            items=items,
        )

    async def get_monthly_sales(self) -> MonthlySalesResult:
        """
        GET /api/payments/sales — все оплаченные платежи за текущий
        календарный месяц без фильтров.

        Каждый элемент содержит category ("main"|"extra"|"other") и флаг
        repeat_purchase (per-category). Атрибуцию к продавцу мессенджер
        делает сам — на основе диалогов.
        """
        d = await self._get("/api/payments/sales", params=None, need_auth=True)
        sales: List[Sale] = []
        for it in d.get("payments") or []:
            sales.append(
                Sale(
                    uuid=str(it["uuid"]),
                    user_id=int(it["user_id"]),
                    staff_id=it.get("staff_id"),
                    amount_minor=int(it["amount_minor"]),
                    category=str(it["category"]),
                    repeat_purchase=bool(it.get("repeat_purchase", False)),
                    date_paid=parse_dt(it.get("date_paid")),
                )
            )
        return MonthlySalesResult(
            month_start=parse_dt(d.get("month_start")),
            payments=sales,
        )

    async def confirm_payment(self, uuid: str) -> ConfirmPaymentResult:
        d = await self._get(f"/api/payments/confirm/{uuid}", params=None, need_auth=True)
        return ConfirmPaymentResult(uuid=str(d["uuid"]), status=str(d["status"]))

    async def refund_payment(self, uuid: str, payload: Optional[RefundInput] = None) -> RefundResult:
        body = payload.model_dump() if payload is not None else None
        d = await self._post(f"/api/payments/refund/{uuid}", body, need_auth=True)
        return RefundResult(
            uuid=str(d["uuid"]),
            provider=str(d["provider"]),
            allowed=bool(d["allowed"]),
            message=str(d.get("message", "")),
            status=d.get("status"),
        )

