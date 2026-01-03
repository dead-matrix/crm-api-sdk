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
    """Result of POST /api/users."""
    created: bool


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

