from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskListItem:
    id: int
    text: str


@dataclass
class TaskInfoResult:
    text: str


@dataclass
class TaskLogResult:
    filename: Optional[str]
    content: bytes  # text file content stored as bytes for generality

