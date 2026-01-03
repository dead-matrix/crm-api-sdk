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
class ToolsMediaItem:
    """Элемент медиа в ответе tools - URL видео и Telegram file_id."""
    video_url: str
    file_id: str


@dataclass
class ToolsMediaResult:
    """Результат tools - текст и массив объектов с видео."""
    text: str
    media: List[ToolsMediaItem]
