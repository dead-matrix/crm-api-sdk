from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NoteStaff:
    id: Optional[int]
    name: Optional[str]


@dataclass
class NoteItem:
    staff: NoteStaff
    date: Optional[datetime]
    text: str

