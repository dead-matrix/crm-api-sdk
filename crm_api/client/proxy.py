from __future__ import annotations

from typing import List

from ..exceptions import ConfigError
from ..models import ProxyBindingsResult, ProxyCheckItem, ProxyCheckResult, ProxyItem


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

    async def proxy_bindings(self, user_id: int) -> ProxyBindingsResult:
        """
        Возвращает сводку привязок прокси к аккаунтам пользователя: сколько
        аккаунтов с прокси и без, среднее число аккаунтов на задействованный
        прокси и сколько прокси не привязаны ни к одному аккаунту.
        """
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        d = await self._get("/api/proxy/bindings", params={"user_id": int(user_id)}, need_auth=True)
        return ProxyBindingsResult(
            total_accounts=int(d.get("total_accounts", 0)),
            accounts_with_proxy=int(d.get("accounts_with_proxy", 0)),
            accounts_without_proxy=int(d.get("accounts_without_proxy", 0)),
            total_proxies=int(d.get("total_proxies", 0)),
            proxies_with_accounts=int(d.get("proxies_with_accounts", 0)),
            proxies_without_accounts=int(d.get("proxies_without_accounts", 0)),
            avg_accounts_per_proxy=float(d.get("avg_accounts_per_proxy", 0.0)),
        )

