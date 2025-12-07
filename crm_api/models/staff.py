from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class StaffInfo:
    name: Optional[str]
    role: Optional[str]
    is_active: bool
    access: Optional[dict]

