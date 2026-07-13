from __future__ import annotations

from typing import Optional

from ..exceptions import ConfigError
from ..models import (
    BotBlocksListResult,
    BotBlockUnblockResult,
    BotBlockReportResult,
)


class BotBlocksAPI:
    """Per-bot флаги «пользователь заблокировал бота» (crm_bot_blocks).

    Использование ботом:
      - на старте и раз в час: list_bot_blocks(bot_id) → локальный кэш set(user_ids);
      - при любом действии пользователя из кэша: unblock_bot_block(bot_id, user_id)
        (fire-and-forget) + немедленное удаление из кэша;
      - при 403 на собственной отправке: report_bot_block(bot_id, user_id, error=...).
    """

    async def list_bot_blocks(self, bot_id: int) -> BotBlocksListResult:
        """GET /api/bot-blocks?bot_id=... — все user_id с активным флагом."""
        if bot_id <= 0:
            raise ConfigError("bot_id must be positive integer")
        data = await self._get("/api/bot-blocks", params={"bot_id": int(bot_id)}, need_auth=True)
        return BotBlocksListResult(
            bot_id=int(data["bot_id"]),
            user_ids=[int(x) for x in (data.get("user_ids") or [])],
            count=int(data.get("count") or 0),
        )

    async def unblock_bot_block(self, bot_id: int, user_id: int) -> BotBlockUnblockResult:
        """POST /api/bot-blocks/unblock — снять флаг (идемпотентно).

        removed=False означает, что флага и не было — это тоже успех.
        """
        if bot_id <= 0:
            raise ConfigError("bot_id must be positive integer")
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        data = await self._post(
            "/api/bot-blocks/unblock",
            {"bot_id": int(bot_id), "user_id": int(user_id)},
            need_auth=True,
        )
        return BotBlockUnblockResult(removed=bool(data.get("removed")))

    async def report_bot_block(
        self,
        bot_id: int,
        user_id: int,
        *,
        reason: str = "blocked",
        error: Optional[str] = None,
    ) -> BotBlockReportResult:
        """POST /api/bot-blocks/report — поставить флаг (идемпотентно).

        reason: blocked | deactivated | chat_not_found. Если передан error
        (текст ошибки Telegram), CRM сама классифицирует причину по нему.
        """
        if bot_id <= 0:
            raise ConfigError("bot_id must be positive integer")
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        data = await self._post(
            "/api/bot-blocks/report",
            {"bot_id": int(bot_id), "user_id": int(user_id),
             "reason": reason, "error": error},
            need_auth=True,
        )
        return BotBlockReportResult(added=bool(data.get("added")))
