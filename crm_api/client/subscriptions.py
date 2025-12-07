from __future__ import annotations

from typing import List

from ..exceptions import ConfigError
from ..models import (
    AddAccessInput,
    AddAccessResult,
    AccessPaymentRef,
    AccessStaffRef,
    AccessHistoryItem,
    SubscriptionsHistoryResult,
    AccessDefinitionsResult,
    TransferLinkResult,
)
from ..utils import parse_dt


class SubscriptionsAPI:
    # --------------- Subscriptions ---------------

    async def add_access(self, data: AddAccessInput) -> AddAccessResult:
        payload = data.model_dump(mode="json")
        res_data = await self._post("/api/access/add", payload, need_auth=True)
        return AddAccessResult(
            created=bool(res_data.get("created")),
            id=res_data.get("id"),
            user_id=int(res_data["user_id"]),
            bot_id=int(res_data["bot_id"]),
            action=str(res_data["action"]),
            action_date=parse_dt(res_data.get("action_date")),
            access_end=parse_dt(res_data.get("access_end")),
        )

    async def subscriptions_history(self, user_id: int) -> SubscriptionsHistoryResult:
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        data = await self._get(
            f"/api/users/{user_id}/subscriptions/history", params=None, need_auth=True
        )
        items: List[AccessHistoryItem] = []
        for h in data.get("history") or []:
            pay = h.get("payment")
            staff = h.get("staff")
            payment_ref = (
                AccessPaymentRef(
                    id=pay.get("id"),
                    amount_minor=pay.get("amount_minor"),
                    currency=pay.get("currency"),
                    status=pay.get("status"),
                    date_paid=parse_dt(pay.get("date_paid")),
                )
                if pay
                else None
            )
            staff_ref = (
                AccessStaffRef(
                    id=staff.get("id"),
                    name=staff.get("name"),
                )
                if staff
                else None
            )
            items.append(
                AccessHistoryItem(
                    action=str(h["action"]),
                    bot_id=int(h["bot_id"]),
                    access=h.get("access"),
                    action_date=parse_dt(h.get("action_date")),
                    access_end=parse_dt(h.get("access_end")),
                    payment=payment_ref,
                    staff=staff_ref,
                    ref=h.get("ref"),
                )
            )
        return SubscriptionsHistoryResult(user_id=int(data["user_id"]), history=items)

    async def access_definitions(self) -> AccessDefinitionsResult:
        d = await self._get("/api/access/definitions", params=None, need_auth=True)
        return AccessDefinitionsResult(main=d.get("main") or {}, poster=d.get("poster") or {})

    async def subscriptions_transfer_link(self, user_id: int, bot_id: int) -> TransferLinkResult:
        if user_id <= 0 or bot_id <= 0:
            raise ConfigError("user_id and bot_id must be positive integers")
        params = {"user_id": int(user_id), "bot_id": int(bot_id)}
        d = await self._post(
            "/api/subscriptions/transfer-link", json_body=None, need_auth=True, params=params
        )
        return TransferLinkResult(transfer_link=str(d["transfer_link"]))

