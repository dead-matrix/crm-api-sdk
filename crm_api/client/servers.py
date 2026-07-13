from __future__ import annotations

from ..exceptions import ConfigError
from ..models import ServerRestartResult, ServerStatusResult


class ServersAPI:
    # --------------- Servers ---------------

    async def servers_restart(self, user_id: int, bot_id: int = 1) -> ServerRestartResult:
        d = await self._post(
            "/api/servers/restart",
            json_body=None,
            need_auth=True,
            params={"user_id": int(user_id), "bot_id": int(bot_id)},
        )
        return ServerRestartResult(message=str(d.get("message", "")))

    async def servers_status(self, user_id: int, bot_id: int = 1) -> ServerStatusResult:
        """
        Готовность воркера пользователя — чтобы опрашивать фактическое
        завершение перезапуска, а не доверять ответу servers_restart
        (он возвращается сразу после приёма команды open, до реального
        подъёма воркера). Лёгкое чтение — безопасно поллить в цикле.
        """
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        if bot_id <= 0:
            raise ConfigError("bot_id must be positive integer")
        d = await self._get(
            "/api/servers/status",
            params={"user_id": int(user_id), "bot_id": int(bot_id)},
            need_auth=True,
        )
        return ServerStatusResult(bound=bool(d.get("bound")), up=bool(d.get("up")))

