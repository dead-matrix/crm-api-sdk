from __future__ import annotations

from ..models import (
    ProfileStatistics,
    PosterAccount,
    PosterSubscription,
    Bot3Summary,
)
from ..utils import parse_dt


class ProfileAPI:
    # --------------- Profile ---------------

    async def profile_statistics(self, user_id: int) -> ProfileStatistics:
        d = await self._get("/api/profile/statistics", params={"user_id": int(user_id)}, need_auth=True)
        return ProfileStatistics(
            subscriber=bool(d.get("subscriber")),
            all_accounts_amount=int(d.get("all_accounts_amount", 0)),
            all_invited=int(d.get("all_invited", 0)),
            all_commented=int(d.get("all_commented", 0)),
            all_stories=int(d.get("all_stories", 0)),
            all_tagged=int(d.get("all_tagged", 0)),
            all_views=int(d.get("all_views", 0)),
            all_reactions=int(d.get("all_reactions", 0)),
            tasks=int(d.get("tasks", 0)),
            valid=int(d.get("valid", 0)),
            work=int(d.get("work", 0)),
            invalid=int(d.get("invalid", 0)),
            spam_block=int(d.get("spam_block", 0)),
            invited=int(d.get("invited", 0)),
            commented=int(d.get("commented", 0)),
            stories=int(d.get("stories", 0)),
            tagged=int(d.get("tagged", 0)),
            views=int(d.get("views", 0)),
            reactions=int(d.get("reactions", 0)),
            quota=d.get("quota"),
        )

    async def profile_bot3_summary(self, user_id: int) -> Bot3Summary:
        d = await self._get("/api/profile/bot3/summary", params={"user_id": int(user_id)}, need_auth=True)
        sub = d.get("subscription") or {}
        acc = d.get("account")
        subscription = PosterSubscription(
            active=bool(sub.get("active")),
            access=sub.get("access"),
            access_end=parse_dt(sub.get("access_end")),
        )
        account = None
        if acc:
            account = PosterAccount(
                telegram_id=acc.get("telegram_id"),
                valid=bool(acc.get("valid")),
                is_connected=bool(acc.get("is_connected")),
                last_connection=parse_dt(acc.get("last_connection")),
                premium=bool(acc.get("premium")),
                full_name=acc.get("full_name"),
                username=acc.get("username"),
                location=acc.get("location"),
            )
        return Bot3Summary(subscription=subscription, account=account, tasks=d.get("tasks") or {})

