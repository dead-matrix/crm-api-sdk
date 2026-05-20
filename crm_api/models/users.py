from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional


@dataclass
class UserBotInfo:
    bot_id: int
    bot_name: str
    registered: Optional[datetime]
    refer: Optional[str]
    access: Optional[Any]
    access_end: Optional[datetime]


@dataclass
class GetUserResult:
    user_id: int
    full_name: Optional[str]
    username: Optional[str]
    status: Optional[str]
    bots_info: List[UserBotInfo]


@dataclass
class CreateUserResult:
    """
    Result of POST /api/users (идемпотентный).

    Если регистрация (user_id, bot_id) уже существовала — `created=False`,
    поля заполнены существующими данными без побочных эффектов.
    Иначе — `created=True`, поля заполнены созданной записью.

    full_name nullable: на идемпотентном пути сервер возвращает
    `user.full_name` напрямую из БД, где поле технически nullable.
    Для свежесозданной записи full_name всегда не-None.
    """
    created: bool
    user_id: int
    full_name: Optional[str]
    username: Optional[str]
    bot_id: int
    refer: Optional[str]
    date_reg: Optional[datetime]


@dataclass
class ListUserItem:
    """
    Элемент списка пользователей бота (GET /api/users?bot_id=...).

    full_name nullable: сервер возвращает `user.full_name` напрямую из
    БД, где поле технически nullable.
    """
    user_id: int
    full_name: Optional[str]
    username: Optional[str]
    date_reg: Optional[datetime]
    refer: Optional[str]
    restricted: bool


@dataclass
class ListUsersResult:
    """Результат GET /api/users?bot_id=...&limit=...&offset=..."""
    bot_id: int
    limit: int
    offset: int
    count: int
    items: List[ListUserItem]


@dataclass
class UpdateUserResult:
    """Result of PUT /api/users/{user_id}."""
    user_id: int
    full_name: str
    username: Optional[str]


@dataclass
class AddAccessResult:
    """Result of POST /api/access/add."""
    created: bool
    id: Optional[int]
    user_id: int
    bot_id: int
    action: str
    action_date: Optional[datetime]
    access_end: Optional[datetime]


@dataclass
class ExtendAccessResult:
    """Result of POST /api/users/{user_id}/access/extend."""
    user_id: int
    access_end: Optional[datetime]


@dataclass
class ExtendAiLimitResult:
    """Result of POST /api/users/{user_id}/ai-limit/extend."""
    previous_ai_limit: int
    ai_limit: int

