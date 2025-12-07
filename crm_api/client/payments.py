from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..models import (
    PaymentsCalculateInput,
    PaymentsCalculateResult,
    CalcItem,
    InvoiceDraftInput,
    InvoiceDraftResult,
    InvoiceIssueInput,
    InvoiceIssueResult,
    PaymentHistoryItem,
    ActivationLink,
    ConfirmPaymentResult,
    RefundInput,
    RefundResult,
    InvoiceInfoResult,
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
        d = await self._post("/api/payments/invoice/draft", data.model_dump(), need_auth=True)
        return InvoiceDraftResult(uuid=str(d["uuid"]), pay_link=str(d["pay_link"]), status=str(d["status"]))

    async def issue_invoice(self, data: InvoiceIssueInput) -> InvoiceIssueResult:
        d = await self._post("/api/payments/invoice/issue", data.model_dump(), need_auth=True)
        return InvoiceIssueResult(pay_url=str(d["pay_url"]), status=str(d["status"]))
    async def get_invoice_info(self, uuid: str) -> InvoiceInfoResult:
        """
        Проверка существования и получение информации о платеже по UUID.
        Не обращается к провайдеру - только данные из БД.
        Можно использовать для валидации UUID до указания email и выставления счета.
        """
        d = await self._get(f"/api/payments/invoice/{uuid}", params=None, need_auth=True)
        return InvoiceInfoResult(
            uuid=str(d["uuid"]),
            status=str(d["status"]),
            status_ru=str(d["status_ru"]),
            client_id=int(d["client_id"]),
            amount_minor=int(d["amount_minor"]),
            currency=str(d.get("currency", "RUB")),
            discount_percent=d.get("discount_percent"),
            description=str(d["description"]),
            items=d.get("items") or [],
            provider=str(d["provider"]),
            pay_link=d.get("pay_link"),
            date_create=parse_dt(d.get("date_create")),
        )

    async def get_payments(self, user_id: int) -> List[PaymentHistoryItem]:
        arr = await self._get(f"/api/payments/{user_id}", params=None, need_auth=True)
        items: List[PaymentHistoryItem] = []
        for p in arr or []:
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
                    date_create=parse_dt(p.get("date_create")),
                    date_invoiced=parse_dt(p.get("date_invoiced")),
                    date_paid=parse_dt(p.get("date_paid")),
                    status=str(p.get("status")),
                    amount_minor=int(p.get("amount_minor", 0)),
                    discount_percent=int(p.get("discount_percent", 0)),
                    currency=str(p.get("currency", "RUB")),
                    items=p.get("items") or [],
                    client_email=p.get("client_email"),
                    pay_url=p.get("pay_url"),
                    provider=p.get("provider"),
                    activation=activation,
                )
            )
        return items

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

