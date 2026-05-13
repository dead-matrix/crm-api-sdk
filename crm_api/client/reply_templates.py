"""
API мультимедийных шаблонов быстрых ответов: `/api/reply-templates`.

Эндпоинты:
- GET    /api/reply-templates           — список (personal-usage sort)
- GET    /api/reply-templates/{id}      — полный шаблон + инкремент usage
- POST   /api/reply-templates           — создание
- DELETE /api/reply-templates/{id}      — удаление (только creator)

Поведение API зеркалит legacy /scripts (общие шаблоны, персональный
ranking по employee_id, system creator → имя "TraffSoft"), но
поддерживает несколько типов содержимого: text/photo/video/gif/voice/
video_note/sticker/file и медиа-альбомы из photo/video/gif.

Источник правды для отправки медиа — `media_object_key` (стабильный S3-
ключ); presigned URL генерирует мессенджер на свою сторону.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import ConfigError
from ..models import (
    DeleteReplyTemplateResult,
    ReplyTemplateCreator,
    ReplyTemplateFull,
    ReplyTemplateItem,
    ReplyTemplateListItem,
    ReplyTemplatePreview,
    REPLY_TEMPLATE_ALBUM_ITEM_TYPES,
    REPLY_TEMPLATE_ALBUM_MAX_ITEMS,
    REPLY_TEMPLATE_ALBUM_MIN_ITEMS,
    REPLY_TEMPLATE_CAPTION_MAX,
    REPLY_TEMPLATE_ITEM_MAX_POS,
    REPLY_TEMPLATE_ITEM_TYPE_TEXT,
    REPLY_TEMPLATE_ITEM_TYPES,
    REPLY_TEMPLATE_KIND_ALBUM,
    REPLY_TEMPLATE_KIND_SINGLE,
    REPLY_TEMPLATE_NO_CAPTION_ITEM_TYPES,
    REPLY_TEMPLATE_TITLE_MAX_LENGTH,
)
from ..utils import parse_dt


class ReplyTemplatesAPI:
    """API для работы с мультимедийными шаблонами быстрых ответов."""

    async def reply_templates_list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ReplyTemplateListItem]:
        """
        Возвращает список шаблонов, отсортированный по usage_count DESC,
        id ASC. Ранжирование персональное — учитывает счётчики
        использования текущего сотрудника.

        Args:
            limit: Максимум записей (>=1). None → серверный default.
            offset: Смещение (>=0). None → 0.
        """
        if limit is not None and limit <= 0:
            raise ConfigError("limit must be positive integer when provided")
        if offset is not None and offset < 0:
            raise ConfigError("offset must be non-negative integer")

        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = int(limit)
        if offset is not None:
            params["offset"] = int(offset)

        data = await self._get(
            "/api/reply-templates",
            params=params or None,
            need_auth=True,
        )
        return [_map_list_item(row) for row in (data or [])]

    async def reply_templates_get(self, template_id: int) -> ReplyTemplateFull:
        """
        Возвращает полный шаблон + items[] (sorted by position).
        Инкрементирует персональный usage_count на стороне CRM.
        """
        if template_id <= 0:
            raise ConfigError("template_id must be positive integer")

        data = await self._get(
            f"/api/reply-templates/{template_id}",
            params=None,
            need_auth=True,
        )
        return _map_full(data)

    async def reply_templates_create(
        self,
        *,
        title: str,
        kind: str,
        items: List[ReplyTemplateItem],
    ) -> ReplyTemplateFull:
        """
        Создаёт шаблон. Валидация дублирует серверную, чтобы дать
        быструю обратную связь без round-trip.
        """
        items = [_normalize_item(it) for it in items]
        _validate_create(title=title.strip() if title else title, kind=kind, items=items)

        payload: Dict[str, Any] = {
            "title": title.strip(),
            "kind": kind,
            "items": [_serialize_item(it) for it in items],
        }
        data = await self._post(
            "/api/reply-templates",
            payload,
            need_auth=True,
        )
        return _map_full(data)

    async def reply_templates_delete(self, template_id: int) -> DeleteReplyTemplateResult:
        """
        Удаляет шаблон. На стороне CRM разрешено только creator'у —
        non-creator получает 403 → AuthError.
        """
        if template_id <= 0:
            raise ConfigError("template_id must be positive integer")

        data = await self._delete(
            f"/api/reply-templates/{template_id}",
            need_auth=True,
        )
        return DeleteReplyTemplateResult(
            id=int(data["id"]),
            public_id=str(data["publicId"]),
        )


# ───────────────── mapping helpers ─────────────────


def _map_creator(raw: Dict[str, Any] | None) -> ReplyTemplateCreator:
    raw = raw or {}
    return ReplyTemplateCreator(
        employee_id=int(raw.get("employeeId", 0)),
        name=raw.get("name"),
    )


def _map_preview(raw: Dict[str, Any] | None) -> ReplyTemplatePreview:
    raw = raw or {}
    return ReplyTemplatePreview(
        first_item_type=raw.get("firstItemType"),
        caption_excerpt=raw.get("captionExcerpt"),
        items_count=int(raw.get("itemsCount", 0)),
    )


def _map_item(raw: Dict[str, Any]) -> ReplyTemplateItem:
    return ReplyTemplateItem(
        position=int(raw.get("position", 0)),
        type=str(raw.get("type", "")),
        caption=raw.get("caption"),
        media_object_key=raw.get("mediaObjectKey"),
        mime=raw.get("mime"),
        size_bytes=raw.get("sizeBytes"),
        duration_ms=raw.get("durationMs"),
        width=raw.get("width"),
        height=raw.get("height"),
        file_name=raw.get("fileName"),
        origin_tenant_id=raw.get("originTenantId"),
        origin_message_id=raw.get("originMessageId"),
    )


def _map_list_item(raw: Dict[str, Any]) -> ReplyTemplateListItem:
    return ReplyTemplateListItem(
        id=int(raw["id"]),
        public_id=str(raw["publicId"]),
        title=str(raw["title"]),
        kind=str(raw["kind"]),
        creator=_map_creator(raw.get("creator")),
        preview=_map_preview(raw.get("preview")),
        usage_count=int(raw.get("usageCount", 0)),
        last_used_at=parse_dt(raw.get("lastUsedAt")),
        created_at=parse_dt(raw.get("createdAt")),
        updated_at=parse_dt(raw.get("updatedAt")),
    )


def _map_full(raw: Dict[str, Any]) -> ReplyTemplateFull:
    items_raw = raw.get("items") or []
    return ReplyTemplateFull(
        id=int(raw["id"]),
        public_id=str(raw["publicId"]),
        title=str(raw["title"]),
        kind=str(raw["kind"]),
        creator=_map_creator(raw.get("creator")),
        items=[_map_item(it) for it in items_raw],
        created_at=parse_dt(raw.get("createdAt")),
        updated_at=parse_dt(raw.get("updatedAt")),
    )


def _serialize_item(it: ReplyTemplateItem) -> Dict[str, Any]:
    """
    Сериализуем item в JSON-форму CRM API (camelCase). None-поля
    опускаем, чтобы не отправлять null'ы.
    """
    out: Dict[str, Any] = {
        "position": it.position,
        "type": it.type,
    }
    if it.caption is not None:
        out["caption"] = it.caption
    if it.media_object_key is not None:
        out["mediaObjectKey"] = it.media_object_key
    if it.mime is not None:
        out["mime"] = it.mime
    if it.size_bytes is not None:
        out["sizeBytes"] = it.size_bytes
    if it.duration_ms is not None:
        out["durationMs"] = it.duration_ms
    if it.width is not None:
        out["width"] = it.width
    if it.height is not None:
        out["height"] = it.height
    if it.file_name is not None:
        out["fileName"] = it.file_name
    if it.origin_tenant_id is not None:
        out["originTenantId"] = it.origin_tenant_id
    if it.origin_message_id is not None:
        out["originMessageId"] = it.origin_message_id
    return out


# ───────────────── validation ─────────────────


def _normalize_item(it: ReplyTemplateItem) -> ReplyTemplateItem:
    """Тримим строки, сохраняя None vs пустую строку."""
    return ReplyTemplateItem(
        position=it.position,
        type=it.type.strip() if it.type else it.type,
        caption=it.caption.strip() if it.caption is not None else None,
        media_object_key=(it.media_object_key.strip()
                          if it.media_object_key is not None else None),
        mime=it.mime,
        size_bytes=it.size_bytes,
        duration_ms=it.duration_ms,
        width=it.width,
        height=it.height,
        file_name=it.file_name.strip() if it.file_name is not None else None,
        origin_tenant_id=it.origin_tenant_id,
        origin_message_id=it.origin_message_id,
    )


def _validate_create(
    *,
    title: str,
    kind: str,
    items: List[ReplyTemplateItem],
) -> None:
    if not title:
        raise ConfigError("title must not be empty")
    if len(title) > REPLY_TEMPLATE_TITLE_MAX_LENGTH:
        raise ConfigError(
            f"title must be at most {REPLY_TEMPLATE_TITLE_MAX_LENGTH} characters"
        )
    if kind not in (REPLY_TEMPLATE_KIND_SINGLE, REPLY_TEMPLATE_KIND_ALBUM):
        raise ConfigError(
            f"kind must be {REPLY_TEMPLATE_KIND_SINGLE!r} or {REPLY_TEMPLATE_KIND_ALBUM!r}"
        )
    if not items:
        raise ConfigError("items must contain at least one element")
    if len(items) > REPLY_TEMPLATE_ALBUM_MAX_ITEMS:
        raise ConfigError(
            f"items must contain at most {REPLY_TEMPLATE_ALBUM_MAX_ITEMS} elements"
        )

    # Per-item shape
    for it in items:
        if it.type not in REPLY_TEMPLATE_ITEM_TYPES:
            raise ConfigError(f"item type {it.type!r} is not supported")
        if it.position < 0 or it.position > REPLY_TEMPLATE_ITEM_MAX_POS:
            raise ConfigError(
                f"item position must be in 0..{REPLY_TEMPLATE_ITEM_MAX_POS} "
                f"(got {it.position})"
            )
        if it.caption is not None and len(it.caption) > REPLY_TEMPLATE_CAPTION_MAX:
            raise ConfigError(
                f"item caption must be at most {REPLY_TEMPLATE_CAPTION_MAX} characters"
            )
        if it.type == REPLY_TEMPLATE_ITEM_TYPE_TEXT:
            if not it.caption:
                raise ConfigError("text item requires non-empty caption")
            if it.media_object_key:
                raise ConfigError("text item must not carry media_object_key")
            for fld_name, fld_val in (
                ("mime", it.mime), ("size_bytes", it.size_bytes),
                ("duration_ms", it.duration_ms), ("width", it.width),
                ("height", it.height), ("file_name", it.file_name),
            ):
                if fld_val is not None:
                    raise ConfigError(f"text item must not carry {fld_name}")
        else:
            if not it.media_object_key:
                raise ConfigError(f"{it.type} item requires media_object_key")
            if it.type in REPLY_TEMPLATE_NO_CAPTION_ITEM_TYPES and it.caption:
                raise ConfigError(f"{it.type} item must not carry caption")

    # Positions: contiguous 0..N-1, no duplicates
    positions = [it.position for it in items]
    if len(set(positions)) != len(positions):
        raise ConfigError("duplicate position in items")
    if sorted(positions) != list(range(len(items))):
        raise ConfigError(f"positions must be contiguous 0..{len(items) - 1}")

    # Kind-specific
    if kind == REPLY_TEMPLATE_KIND_SINGLE:
        if len(items) != 1:
            raise ConfigError("single template requires exactly 1 item")
    else:  # album
        if len(items) < REPLY_TEMPLATE_ALBUM_MIN_ITEMS:
            raise ConfigError(
                f"album requires at least {REPLY_TEMPLATE_ALBUM_MIN_ITEMS} items"
            )
        for it in items:
            if it.type not in REPLY_TEMPLATE_ALBUM_ITEM_TYPES:
                raise ConfigError(
                    f"album item type must be one of photo/video/gif "
                    f"(got {it.type!r} at position {it.position})"
                )
            if it.position != 0 and it.caption:
                raise ConfigError(
                    f"caption only allowed at position=0 in album "
                    f"(found at position {it.position})"
                )
