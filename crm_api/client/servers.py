from __future__ import annotations

from ..models import ServerRestartResult


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

