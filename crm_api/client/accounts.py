from __future__ import annotations

from typing import List

from ..models import AccountItem, DayTotal
from ..exceptions import ConfigError


class AccountsAPI:
    # --------------- Accounts ---------------

    async def accounts_list(self, user_id: int) -> List[AccountItem]:
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        items: List[AccountItem] = []
        res = await self._get("/api/accounts/list", params={"user_id": int(user_id)}, need_auth=True)
        for a in res or []:
            items.append(
                AccountItem(
                    session_name=a.get("session_name"),
                    valid=bool(a.get("valid")),
                    spam_block=bool(a.get("spam_block")),
                    is_connected=bool(a.get("is_connected")),
                    location=a.get("location"),
                    full_name=a.get("full_name"),
                    username=a.get("username"),
                    phone=a.get("phone"),
                    premium=bool(a.get("premium")),
                    commented=DayTotal(
                        day=int(a.get("commented", {}).get("day", 0)),
                        total=int(a.get("commented", {}).get("total", 0)),
                    ),
                    invited=DayTotal(
                        day=int(a.get("invited", {}).get("day", 0)),
                        total=int(a.get("invited", {}).get("total", 0)),
                    ),
                    stories=DayTotal(
                        day=int(a.get("stories", {}).get("day", 0)),
                        total=int(a.get("stories", {}).get("total", 0)),
                    ),
                    tagged=DayTotal(
                        day=int(a.get("tagged", {}).get("day", 0)),
                        total=int(a.get("tagged", {}).get("total", 0)),
                    ),
                    views=DayTotal(
                        day=int(a.get("views", {}).get("day", 0)),
                        total=int(a.get("views", {}).get("total", 0)),
                    ),
                    reactions=DayTotal(
                        day=int(a.get("reactions", {}).get("day", 0)),
                        total=int(a.get("reactions", {}).get("total", 0)),
                    ),
                )
            )
        return items
