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
    ListUserItem,
    ListUsersResult,
    ExtendAccessResult,
    ExtendAiLimitResult,
)
from ..utils import parse_dt


class UsersAPI:
    # --------------- Users/Subs basic ---------------

    async def create_user(self, data: CreateUserInput) -> CreateUserResult:
        """
        POST /api/users — идемпотентное создание пользователя.

        Если регистрация (user_id, bot_id) уже существует → `created=False`,
        возвращаются существующие данные без побочных эффектов.
        Иначе создаются `User`/`BotRegistration`/`Dialog` и `created=True`.
        """
        payload = data.model_dump()
        res_data = await self._post("/api/users", payload, need_auth=True)
        return CreateUserResult(
            created=bool(res_data.get("created")),
            user_id=int(res_data["user_id"]),
            # full_name nullable на идемпотентном пути; не оборачиваем в str(),
            # иначе None превратится в строку "None".
            full_name=res_data.get("full_name"),
            username=res_data.get("username"),
            bot_id=int(res_data["bot_id"]),
            refer=res_data.get("refer"),
            date_reg=parse_dt(res_data.get("date_reg")),
        )

    async def list_users(
        self,
        bot_id: int,
        limit: int = 100_000,
        offset: int = 0,
    ) -> ListUsersResult:
        """
        GET /api/users?bot_id=...&limit=...&offset=... — список пользователей
        бота с пагинацией.

        Args:
            bot_id: ID бота (>= 1) — обязательный фильтр
            limit: Максимум записей (>= 1, default 100_000)
            offset: Смещение (>= 0, default 0)

        Returns:
            ListUsersResult с полями bot_id, limit, offset, count и items.
            Каждый item содержит `restricted: bool` — флаг блокировки.
        """
        if bot_id <= 0:
            raise ConfigError("bot_id must be positive integer")
        if limit <= 0:
            raise ConfigError("limit must be positive integer")
        if offset < 0:
            raise ConfigError("offset must be non-negative integer")

        params = {"bot_id": int(bot_id), "limit": int(limit), "offset": int(offset)}
        data = await self._get("/api/users", params=params, need_auth=True)
        items: List[ListUserItem] = []
        for it in data.get("items") or []:
            items.append(
                ListUserItem(
                    user_id=int(it["user_id"]),
                    # full_name nullable в БД; передаём как есть.
                    full_name=it.get("full_name"),
                    username=it.get("username"),
                    date_reg=parse_dt(it.get("date_reg")),
                    refer=it.get("refer"),
                    restricted=bool(it.get("restricted", False)),
                )
            )
        return ListUsersResult(
            bot_id=int(data["bot_id"]),
            limit=int(data["limit"]),
            offset=int(data["offset"]),
            count=int(data["count"]),
            items=items,
        )

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

