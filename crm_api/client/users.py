from __future__ import annotations

from typing import List

from ..exceptions import ConfigError
from ..models import (
    CreateUserInput,
    UpdateUserInput,
    CreateUserResult,
    UpdateUserResult,
    UserBotInfo,
    GetUserResult,
    ExtendAccessResult,
    ExtendAiLimitResult,
)
from ..utils import parse_dt


class UsersAPI:
    # --------------- Users/Subs basic ---------------

    async def create_user(self, data: CreateUserInput) -> CreateUserResult:
        payload = data.model_dump()
        res_data = await self._post("/api/users", payload, need_auth=True)
        created = bool(res_data.get("created"))
        return CreateUserResult(created=created)

    async def update_user(self, user_id: int, data: UpdateUserInput) -> UpdateUserResult:
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        payload = data.model_dump()
        res_data = await self._put(f"/api/users/{user_id}", payload, need_auth=True)
        return UpdateUserResult(
            user_id=int(res_data["user_id"]),
            full_name=str(res_data["full_name"]),
            username=res_data.get("username"),
        )

    async def get_user(self, user_id: int) -> GetUserResult:
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        data = await self._get(f"/api/users/{user_id}", params=None, need_auth=True)
        bots_info: List[UserBotInfo] = []
        for item in data.get("bots_info") or []:
            bots_info.append(
                UserBotInfo(
                    bot_id=int(item["bot_id"]),
                    bot_name=str(item["bot_name"]),
                    registered=parse_dt(item.get("registered")),
                    refer=item.get("refer"),
                    access=item.get("access"),
                    access_end=parse_dt(item.get("access_end")),
                )
            )
        return GetUserResult(
            user_id=int(data["user_id"]),
            full_name=data.get("full_name"),
            username=data.get("username"),
            status=data.get("status"),
            bots_info=bots_info,
        )

    async def extend_user_access(self, user_id: int, bot_id: int, days: int) -> ExtendAccessResult:
        """
        POST /api/users/{user_id}/access/extend — добавляет дни доступа пользователю.

        Args:
            user_id: ID пользователя Telegram (>= 1)
            bot_id: ID бота (1 = MainBot, 3 = Poster)
            days: Количество дней для добавления (>= 1)

        Returns:
            ExtendAccessResult с user_id и новой датой окончания доступа
        """
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        if bot_id <= 0:
            raise ConfigError("bot_id must be positive integer")
        if days <= 0:
            raise ConfigError("days must be positive integer")

        params = {"bot_id": int(bot_id), "days": int(days)}
        data = await self._post(f"/api/users/{user_id}/access/extend", None, need_auth=True, params=params)
        return ExtendAccessResult(
            user_id=int(data["user_id"]),
            access_end=parse_dt(data.get("access_end")),
        )

    async def extend_ai_limit(self, user_id: int, millions: int) -> ExtendAiLimitResult:
        """
        POST /api/users/{user_id}/ai-limit/extend — расширяет AI квоту пользователю.

        Добавляет указанное количество миллионов символов к текущему лимиту ai_limit.

        Args:
            user_id: ID пользователя Telegram (>= 1)
            millions: Количество миллионов символов для добавления (>= 1)

        Returns:
            ExtendAiLimitResult с предыдущим и новым значением ai_limit
        """
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        if millions <= 0:
            raise ConfigError("millions must be positive integer")

        params = {"millions": int(millions)}
        data = await self._post(f"/api/users/{user_id}/ai-limit/extend", None, need_auth=True, params=params)
        return ExtendAiLimitResult(
            previous_ai_limit=int(data["previous_ai_limit"]),
            ai_limit=int(data["ai_limit"]),
        )

