from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import ConfigError
from ..models import (
    ReferreePayment,
    ReferreeInfo,
    ReferralsInfoResult,
    WithdrawRequestResult,
    WithdrawSettleResult,
)
from ..utils import parse_dt

# Методы вывода реф-баланса: 'wallet' (на кошелёк) | 'subscription' (в обмен на подписку).
WITHDRAW_METHODS = frozenset({"wallet", "subscription"})


class ReferralsAPI:
    # --------------- Referrals ---------------

    async def referrals_info(self, user_id: int) -> ReferralsInfoResult:
        d = await self._get("/api/referrals/info", params={"user_id": int(user_id)}, need_auth=True)
        referrees: List[ReferreeInfo] = []
        for r in d.get("referrees") or []:
            pays: List[ReferreePayment] = []
            for p in r.get("payments") or []:
                pays.append(
                    ReferreePayment(
                        date=parse_dt(p.get("date")),
                        amount_minor=int(p.get("amount_minor", 0)),
                        commission_usd=float(p.get("commission_usd", 0.0)),
                        status=str(p.get("status")),
                    )
                )
            referrees.append(
                ReferreeInfo(
                    user_id=int(r.get("user_id")),
                    full_name=r.get("full_name"),
                    username=r.get("username"),
                    payments_count=int(r.get("payments_count", 0)),
                    payments_sum_minor=int(r.get("payments_sum_minor", 0)),
                    payments=pays,
                )
            )
        return ReferralsInfoResult(
            ref_link=str(d.get("ref_link")),
            percent=int(d.get("percent", 0)),
            registrations=int(d.get("registrations", 0)),
            ref_payments=int(d.get("ref_payments", 0)),
            ref_total_sum=int(d.get("ref_total_sum", 0)),
            earned_usd=float(d.get("earned_usd", 0.0)),
            available_usd=float(d.get("available_usd", 0.0)),
            referrees=referrees,
        )

    # --------------- Withdrawals ---------------

    async def referrals_withdraw_request(self, user_id: int, method: str) -> WithdrawRequestResult:
        """
        Заявка реферера на вывод всего доступного баланса.

        method: 'wallet' | 'subscription'. Ответ status: 'no_balance' |
        'already_pending' (бот: call.answer show_alert) | 'created'.
        """
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        m = (method or "").strip().lower()
        if m not in WITHDRAW_METHODS:
            raise ConfigError("method must be 'wallet' or 'subscription'")

        d = await self._post(
            "/api/referrals/withdraw/request",
            {"user_id": int(user_id), "method": m},
            need_auth=True,
        )
        return WithdrawRequestResult(
            status=str(d.get("status")),
            withdrawal_id=int(d["withdrawal_id"]) if d.get("withdrawal_id") is not None else None,
            amount_usd=float(d["amount_usd"]) if d.get("amount_usd") is not None else None,
            method=d.get("method"),
            available_usd=float(d["available_usd"]) if d.get("available_usd") is not None else None,
        )

    async def referrals_withdraw_settle(
        self,
        user_id: int,
        amount_minor: int,
        method: str,
        withdrawal_id: Optional[int] = None,
    ) -> WithdrawSettleResult:
        """
        Провести вывод: перевести amount_minor (USD-центы) из 'доступно' в
        'выплачено' и зафиксировать method. Поддерживает частичный вывод.

        withdrawal_id — закрыть конкретную заявку (опционально; иначе закрывается
        открытая заявка пользователя либо создаётся запись вывода).
        """
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        if amount_minor <= 0:
            raise ConfigError("amount_minor must be positive integer (USD cents)")
        m = (method or "").strip().lower()
        if m not in WITHDRAW_METHODS:
            raise ConfigError("method must be 'wallet' or 'subscription'")

        payload: Dict[str, Any] = {
            "user_id": int(user_id),
            "amount_minor": int(amount_minor),
            "method": m,
        }
        if withdrawal_id is not None:
            payload["withdrawal_id"] = int(withdrawal_id)

        d = await self._post("/api/referrals/withdraw/settle", payload, need_auth=True)
        return WithdrawSettleResult(
            status=str(d.get("status")),
            withdrawal_id=int(d.get("withdrawal_id")),
            paid_usd=float(d.get("paid_usd", 0.0)),
            available_after_usd=float(d.get("available_after_usd", 0.0)),
            method=str(d.get("method")),
        )

