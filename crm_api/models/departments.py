from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DepartmentItem:
    id: int
    name: str
    title: str

