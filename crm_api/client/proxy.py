from __future__ import annotations

from typing import List

from ..models import ProxyCheckItem, ProxyCheckResult, ProxyItem


class ProxyAPI:
    # --------------- Proxy ---------------

    async def proxy_check(self, user_id: int) -> ProxyCheckResult:
        d = await self._post("/api/proxy/check", None, need_auth=True, params={"user_id": int(user_id)})
        items: List[ProxyCheckItem] = []
        for r in d.get("results") or []:
            items.append(
                ProxyCheckItem(
                    proxy=str(r.get("proxy")),
                    valid=bool(r.get("valid")),
                    ru_error=r.get("ru_error"),
                    location=r.get("location"),
                )
            )
        return ProxyCheckResult(
            checked=int(d.get("checked", 0)),
            valid=int(d.get("valid", 0)),
            invalid=int(d.get("invalid", 0)),
            results=items,
        )

    async def proxy_list(self, user_id: int) -> List[ProxyItem]:
        d = await self._get("/api/proxy/list", params={"user_id": int(user_id)}, need_auth=True)
        items: List[ProxyItem] = []
        for r in d or []:
            items.append(
                ProxyItem(
                    type=r.get("type"),
                    ip=r.get("ip"),
                    port=r.get("port"),
                    login=r.get("login"),
                    password=r.get("password"),
                    valid=bool(r.get("valid")),
                    location=r.get("location"),
                )
            )
        return items

