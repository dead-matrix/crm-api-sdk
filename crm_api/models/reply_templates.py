"""
Dataclasses для мультимедийных шаблонов быстрых ответов
(`/api/reply-templates`).

Покрывает list/detail ответы и тело запроса на создание. Для DELETE
возвращается компактный `DeleteReplyTemplateResult`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ───────────────── allowed value constants ─────────────────
# Дублируют серверные значения. Удобно использовать вместо строковых
# литералов на стороне приложения.

REPLY_TEMPLATE_KIND_SINGLE = "single"
REPLY_TEMPLATE_KIND_ALBUM = "album"

REPLY_TEMPLATE_ITEM_TYPE_TEXT = "text"
REPLY_TEMPLATE_ITEM_TYPE_PHOTO = "photo"
REPLY_TEMPLATE_ITEM_TYPE_VIDEO = "video"
REPLY_TEMPLATE_ITEM_TYPE_GIF = "gif"
REPLY_TEMPLATE_ITEM_TYPE_VOICE = "voice"
REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE = "video_note"
REPLY_TEMPLATE_ITEM_TYPE_STICKER = "sticker"
REPLY_TEMPLATE_ITEM_TYPE_FILE = "file"

REPLY_TEMPLATE_ITEM_TYPES = frozenset({
    REPLY_TEMPLATE_ITEM_TYPE_TEXT,
    REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO,
    REPLY_TEMPLATE_ITEM_TYPE_GIF,
    REPLY_TEMPLATE_ITEM_TYPE_VOICE,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE,
    REPLY_TEMPLATE_ITEM_TYPE_STICKER,
    REPLY_TEMPLATE_ITEM_TYPE_FILE,
})

REPLY_TEMPLATE_ALBUM_ITEM_TYPES = frozenset({
    REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO,
    REPLY_TEMPLATE_ITEM_TYPE_GIF,
})

REPLY_TEMPLATE_NO_CAPTION_ITEM_TYPES = frozenset({
    REPLY_TEMPLATE_ITEM_TYPE_VOICE,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE,
    REPLY_TEMPLATE_ITEM_TYPE_STICKER,
})

REPLY_TEMPLATE_TITLE_MAX_LENGTH = 255
REPLY_TEMPLATE_CAPTION_MAX = 4096
REPLY_TEMPLATE_ALBUM_MIN_ITEMS = 2
REPLY_TEMPLATE_ALBUM_MAX_ITEMS = 10
REPLY_TEMPLATE_ITEM_MAX_POS = 9


# ───────────────── data classes ─────────────────


@dataclass
class ReplyTemplateCreator:
    """
    Сотрудник, создавший шаблон. Для системных шаблонов сервер
    подставляет имя "TraffSoft" даже когда `employee_id == 0` и
    собственно записи в staff может не быть.
    """
    employee_id: int
    name: Optional[str]


@dataclass
class ReplyTemplatePreview:
    """Краткое превью для списка шаблонов."""
    first_item_type: Optional[str]
    caption_excerpt: Optional[str]
    items_count: int


@dataclass
class ReplyTemplateListItem:
    """Элемент списка `/api/reply-templates`. items[] намеренно не входит."""
    id: int
    public_id: str
    title: str
    kind: str
    creator: ReplyTemplateCreator
    preview: ReplyTemplatePreview
    usage_count: int
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ReplyTemplateItem:
    """
    Один элемент шаблона.

    type='text': обязателен caption, поля media_* запрещены.
    Прочие типы: обязателен media_object_key (стабильный S3-ключ —
    мессенджер генерирует presigned URL при отправке).
    voice/video_note/sticker: caption запрещён (Telegram его теряет).
    """
    position: int
    type: str
    caption: Optional[str] = None
    media_object_key: Optional[str] = None
    mime: Optional[str] = None
    size_bytes: Optional[int] = None
    duration_ms: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_name: Optional[str] = None
    origin_tenant_id: Optional[str] = None
    origin_message_id: Optional[str] = None


@dataclass
class ReplyTemplateFull:
    """Полный шаблон. items отсортированы по position возрастанию."""
    id: int
    public_id: str
    title: str
    kind: str
    creator: ReplyTemplateCreator
    items: List[ReplyTemplateItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class DeleteReplyTemplateResult:
    """Результат успешного удаления шаблона."""
    id: int
    public_id: str
