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
    # None означает, что активный статус снят (POST /api/dialogs/status
    # был вызван без status_id или с status_id=None).
    status: Optional[str]


@dataclass
class DialogSearchItem:
    """
    Single dialog item from search results.

    status/status_color nullable: сервер шлёт `status_title or default_status_title`,
    и оба могут быть None (диалог без выставленного статуса в департаменте,
    у которого не задан default_status). Паритет с DialogItem.
    """
    user_id: int
    full_name: Optional[str]
    has_active_subscription: bool
    status: Optional[str]
    status_color: Optional[str]


@dataclass
class DialogSearchResult:
    """Result of GET /api/dialogs/{department}/search."""
    dialogs: List[DialogSearchItem]
    limit: int
    offset: int

