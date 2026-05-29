from __future__ import annotations

from dataclasses import dataclass
from typing import List

# Sales-decks dataclasses. До Phase 5 этот модуль также экспортировал
# ``ScriptItem`` и ``ScriptFull`` для legacy text quick replies; они
# удалены вместе с ``scripts_list`` / ``scripts_get`` / ``scripts_create``
# методами клиента после миграции на reply templates.


@dataclass
class PriceMediaItem:
    """Элемент ответа price - текст и массив ссылок на картинки."""
    text: str
    media: List[str]


@dataclass
class ToolsMediaItem:
    """Элемент медиа в ответе tools - URL видео, превью (thumb) и Telegram file_id."""
    video_url: str
    thumb: str
    file_id: str


@dataclass
class ToolsMediaResult:
    """Результат tools - текст и массив объектов с видео."""
    text: str
    media: List[ToolsMediaItem]
