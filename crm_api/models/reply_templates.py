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

    `id` приходит из сервера в read-response, отсутствует в create
    request (сервер назначает сам). Клиенты, кэширующие per-item
    state (например, Telegram file_id cache в мессенджере) обязаны
    ключевать по `id`, не по `position` — последний может поменяться
    при будущих reorder-операциях.
    """
    position: int
    type: str
    id: int = 0
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


# ─────────────── Delivery refs (file-id reuse cache) ───────────────
#
# Кэш повторной отправки media-items в конкретного бота/аккаунт.
# Telegram `file_id` стабилен в пределах одного бота — первая
# отправка достаёт его из ответа Telegram, последующие
# переиспользуют без скачивания файла из S3.

DELIVERY_PROVIDER_TELEGRAM = "telegram"


@dataclass
class DeliveryRef:
    """Одна персистнутая запись (template_item × provider × scope)."""
    id: int
    item_id: int
    provider: str
    provider_scope: str
    media_ref: str
    media_unique_ref: Optional[str] = None
    media_type: Optional[str] = None
    fail_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UpsertDeliveryRefInput:
    """Один элемент batch upsert."""
    item_id: int
    media_ref: str
    media_unique_ref: Optional[str] = None
    media_type: Optional[str] = None


@dataclass
class UpsertDeliveryRefsInput:
    """
    Body PUT /reply-templates/{template_id}/delivery-refs.

    Серверный контракт:
      - provider непустой;
      - provider_scope непустой;
      - refs ∈ [1, 10];
      - каждый item_id принадлежит этому template_id (иначе 422);
      - upsert идемпотентен по (template_item_id, provider, scope);
      - успешный upsert ВСЕГДА сбрасывает server-side fail_count = 0.
    """
    provider: str
    provider_scope: str
    refs: List[UpsertDeliveryRefInput] = field(default_factory=list)
