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





