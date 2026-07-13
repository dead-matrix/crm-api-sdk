from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class BotBlocksListResult:
    """Result of GET /api/bot-blocks: активные флаги «заблокировал бота» по боту."""
    bot_id: int
    user_ids: List[int]
    count: int


@dataclass
class BotBlockUnblockResult:
    """Result of POST /api/bot-blocks/unblock (идемпотентный)."""
    removed: bool


@dataclass
class BotBlockReportResult:
    """Result of POST /api/bot-blocks/report (идемпотентный)."""
    added: bool
