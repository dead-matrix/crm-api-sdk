from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class StaffInfo:
    name: Optional[str]
    role: Optional[str]
    is_active: bool
    access: Optional[dict]


@dataclass
class StaffListItem:
    """Короткая запись сотрудника из `GET /api/staff/list` (user_id > 1000)."""

    user_id: int
    name: str
    role: str

