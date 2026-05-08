from __future__ import annotations

from typing import List

from ..exceptions import ApiError, ConfigError
from ..models import (
    AddAccessInput,
    AddAccessResult,
    AccessPaymentRef,
    AccessStaffRef,
    AccessHistoryItem,
    SubscriptionsHistoryResult,
    AccessDefinitionsResult,
    TransferLinkResult,
    TransferRedeemInput,
    TransferRedeemResult,
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

    async def subscriptions_transfer_link(
        self, user_id: int, bot_id: int
    ) -> TransferLinkResult:
        """
        Получить ссылку переноса доступа.

        Возвращает TransferLinkResult, у которого:
          - при успехе: transfer_link/token/expires_at/bot_id заполнены, error_code=None
          - при ошибке (CRM ответил структурированным error_code): error_code/
            error_message заполнены, transfer_link=None.

        Для бек-совместимости НЕ выбрасывает ApiError для известных
        бизнес-кодов (no_subscription, not_supported, configuration_error и т.п.).
        Транспортные / неизвестные ошибки прокидываются как обычно.
        """
        if user_id <= 0 or bot_id <= 0:
            raise ConfigError("user_id and bot_id must be positive integers")
        params = {"user_id": int(user_id), "bot_id": int(bot_id)}
        try:
            d = await self._post(
                "/api/subscriptions/transfer-link",
                json_body=None,
                need_auth=True,
                params=params,
            )
        except ApiError as e:
            return TransferLinkResult(
                error_code=e.code,
                error_message=str(e) or e.code,
            )
        return TransferLinkResult(
            transfer_link=d.get("transfer_link"),
            token=d.get("token"),
            bot_id=d.get("bot_id"),
            expires_at=parse_dt(d.get("expires_at")),
            ttl_hours=d.get("ttl_hours"),
        )

    async def subscriptions_transfer_redeem(
        self, data: TransferRedeemInput
    ) -> TransferRedeemResult:
        """
        Выполнить redeem transfer-токена. Используется ботом при обработке
        deep-link ?start=TR_...

        Не выбрасывает ApiError на известные бизнес-кодах
        (no_subscription / recipient_has_access / invalid_token / expired /
        wrong_bot / same_user) - возвращает TransferRedeemResult(success=False).

        Транспортные/системные ошибки выбрасываются как обычно.
        """
        if data.recipient_user_id <= 0 or data.bot_id <= 0 or not data.token:
            raise ConfigError(
                "token, recipient_user_id and bot_id must be provided"
            )
        body = {
            "token": str(data.token),
            "recipient_user_id": int(data.recipient_user_id),
            "bot_id": int(data.bot_id),
        }
        try:
            d = await self._post(
                "/api/subscriptions/transfer/redeem",
                json_body=body,
                need_auth=True,
            )
        except ApiError as e:
            return TransferRedeemResult(
                success=False,
                error_code=e.code,
                error_message=str(e) or e.code,
            )
        return TransferRedeemResult(
            success=True,
            source_user_id=d.get("source_user_id"),
            recipient_user_id=d.get("recipient_user_id"),
            bot_id=d.get("bot_id"),
            access=d.get("access"),
            access_end=parse_dt(d.get("access_end")),
        )
