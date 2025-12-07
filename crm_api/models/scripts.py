from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScriptItem:
    """Элемент списка текстовых скриптов."""
    id: int
    title: str
    creator: Optional[str]


@dataclass
class ScriptFull:
    """Полный текст скрипта."""
    id: int
    title: str
    text: str


@dataclass
class PriceMediaItem:
    """Элемент ответа price - текст и массив ссылок на картинки."""
    text: str
    media: List[str]


@dataclass
class ToolsMediaResult:
    """Результат tools - текст и массив ссылок на видео."""
    text: str
    media: List[str]
