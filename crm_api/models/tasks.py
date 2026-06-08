from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskListItem:
    id: int
    text: str
    hide: bool = False


@dataclass
class TaskInfoResult:
    text: str


@dataclass
class TaskLogResult:
    filename: Optional[str]
    content: bytes  # text file content stored as bytes for generality


@dataclass
class ActiveTasksResult:
    """Result of GET /api/tasks/active."""
    text: str  # HTML-formatted text with active tasks info

