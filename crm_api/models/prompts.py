from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptUpdateResult:
    # Возможные варианты:
    # {"reset": bool, "message": str} или {"updated": True} или {"created": True}
    reset: Optional[bool] = None
    message: Optional[str] = None
    updated: Optional[bool] = None
    created: Optional[bool] = None

