from __future__ import annotations

from typing import List

from ..models import (
    ReferreePayment,
    ReferreeInfo,
    ReferralsInfoResult,
)
from ..utils import parse_dt


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

