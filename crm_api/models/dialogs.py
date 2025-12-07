from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DialogItem:
    user_id: int
    full_name: Optional[str]
    has_active_subscription: bool
    status: Optional[str]
    status_color: Optional[str]


@dataclass
class TransferDialogResult:
    transferred: bool


@dataclass
class StatusItem:
    id: int
    title: str
    color: Optional[str]


@dataclass
class StatusesResult:
    department_id: int
    default_status_id: Optional[int]
    statuses: List[StatusItem]


@dataclass
class ChangeStatusResult:
    status: str

