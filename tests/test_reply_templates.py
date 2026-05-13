"""Tests for ReplyTemplatesAPI (/api/reply-templates)."""
from __future__ import annotations

import json
from typing import Any, Dict

import httpx
import pytest

from conftest import error_response, success_response

from crm_api.exceptions import ApiError, AuthError, ConfigError
from crm_api.models import (
    ReplyTemplateItem,
    REPLY_TEMPLATE_ITEM_TYPE_FILE,
    REPLY_TEMPLATE_ITEM_TYPE_GIF,
    REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
    REPLY_TEMPLATE_ITEM_TYPE_TEXT,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE,
    REPLY_TEMPLATE_ITEM_TYPE_VOICE,
    REPLY_TEMPLATE_KIND_ALBUM,
    REPLY_TEMPLATE_KIND_SINGLE,
)


# ───────────────── helpers ─────────────────


def _list_row(
    *,
    id_: int = 1,
    public_id: str = "uuid-1",
    title: str = "Hi",
    kind: str = "single",
    creator_employee: int = 5,
    creator_name: str | None = "Olga",
    preview: Dict[str, Any] | None = None,
    usage_count: int = 0,
    last_used_at: str | None = None,
) -> Dict[str, Any]:
    return {
        "id": id_,
        "publicId": public_id,
        "title": title,
        "kind": kind,
        "creator": {"employeeId": creator_employee, "name": creator_name},
        "preview": preview or {"firstItemType": "text", "captionExcerpt": "hi", "itemsCount": 1},
        "usageCount": usage_count,
        "lastUsedAt": last_used_at,
        "createdAt": "2026-05-13T10:00:00",
        "updatedAt": "2026-05-13T10:00:00",
    }


def _full_row(
    *,
    id_: int = 1,
    public_id: str = "uuid-1",
    title: str = "Hi",
    kind: str = "single",
    items: list[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    return {
        "id": id_,
        "publicId": public_id,
        "title": title,
        "kind": kind,
        "creator": {"employeeId": 5, "name": "Olga"},
        "items": items or [{"position": 0, "type": "text", "caption": "hi"}],
        "createdAt": "2026-05-13T10:00:00",
        "updatedAt": "2026-05-13T10:00:00",
    }


# ───────────────── list ─────────────────


class TestReplyTemplatesList:
    @pytest.mark.asyncio
    async def test_list_maps_rows(self, client_factory):
        routes = {
            "GET /api/reply-templates": lambda req: success_response([
                _list_row(
                    id_=10, public_id="uuid-a", title="Приветствие",
                    kind="single", creator_employee=5, creator_name="Olga",
                    usage_count=7, last_used_at="2026-05-10T12:00:00",
                ),
                _list_row(
                    id_=11, public_id="uuid-b", title="Альбом",
                    kind="album", creator_employee=0, creator_name="TraffSoft",
                    preview={"firstItemType": "photo", "captionExcerpt": "look", "itemsCount": 3},
                ),
            ]),
        }
        async with client_factory(routes) as client:
            items = await client.reply_templates_list(limit=50, offset=10)

        assert len(items) == 2
        a, b = items
        assert (a.id, a.public_id, a.title, a.kind) == (10, "uuid-a", "Приветствие", "single")
        assert a.creator.employee_id == 5
        assert a.creator.name == "Olga"
        assert a.usage_count == 7
        assert a.last_used_at is not None
        assert b.creator.employee_id == 0
        assert b.creator.name == "TraffSoft"
        assert b.preview.first_item_type == "photo"
        assert b.preview.items_count == 3

    @pytest.mark.asyncio
    async def test_list_sends_query_params(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["query"] = dict(req.url.params)
            return success_response([])

        routes = {"GET /api/reply-templates": handler}
        async with client_factory(routes) as client:
            await client.reply_templates_list(limit=25, offset=50)

        assert captured["query"] == {"limit": "25", "offset": "50"}

    @pytest.mark.asyncio
    async def test_list_omits_default_params(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["query"] = dict(req.url.params)
            return success_response([])

        routes = {"GET /api/reply-templates": handler}
        async with client_factory(routes) as client:
            await client.reply_templates_list()

        assert captured["query"] == {}

    @pytest.mark.asyncio
    async def test_list_empty(self, client_factory):
        routes = {"GET /api/reply-templates": lambda req: success_response([])}
        async with client_factory(routes) as client:
            items = await client.reply_templates_list()
        assert items == []

    @pytest.mark.asyncio
    async def test_list_negative_params_validated(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_list(limit=-1)
            with pytest.raises(ConfigError):
                await client.reply_templates_list(offset=-1)


# ───────────────── get ─────────────────


class TestReplyTemplatesGet:
    @pytest.mark.asyncio
    async def test_get_album_maps_items(self, client_factory):
        items = [
            {
                "position": 0, "type": "photo", "caption": "header",
                "mediaObjectKey": "shared/x/0.jpg",
                "mime": "image/jpeg", "sizeBytes": 248123,
                "width": 1280, "height": 960,
                "originTenantId": "t1", "originMessageId": "m9",
            },
            {
                "position": 1, "type": "video",
                "mediaObjectKey": "shared/x/1.mp4",
                "mime": "video/mp4", "sizeBytes": 9999999,
                "durationMs": 15000, "width": 1920, "height": 1080,
            },
            {
                "position": 2, "type": "gif",
                "mediaObjectKey": "shared/x/2.gif",
            },
        ]
        routes = {
            "GET /api/reply-templates/{template_id}":
                lambda req: success_response(_full_row(id_=42, public_id="uuid-42",
                                                        title="Альбом", kind="album", items=items)),
        }
        async with client_factory(routes) as client:
            full = await client.reply_templates_get(42)
        assert full.id == 42 and full.public_id == "uuid-42"
        assert full.kind == "album"
        assert len(full.items) == 3
        assert full.items[0].caption == "header"
        assert full.items[1].duration_ms == 15000
        assert full.items[2].caption is None
        assert full.items[0].origin_message_id == "m9"

    @pytest.mark.asyncio
    async def test_get_single_text(self, client_factory):
        routes = {
            "GET /api/reply-templates/{template_id}":
                lambda req: success_response(_full_row(items=[
                    {"position": 0, "type": "text", "caption": "Привет!"}
                ])),
        }
        async with client_factory(routes) as client:
            full = await client.reply_templates_get(7)
        assert full.kind == "single" and len(full.items) == 1
        it = full.items[0]
        assert it.type == "text" and it.caption == "Привет!"
        assert it.media_object_key is None

    @pytest.mark.asyncio
    async def test_get_validates_id(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_get(0)
            with pytest.raises(ConfigError):
                await client.reply_templates_get(-3)

    @pytest.mark.asyncio
    async def test_get_404_propagates_api_error(self, client_factory):
        routes = {
            "GET /api/reply-templates/{template_id}":
                lambda req: error_response("Reply template not found", status=404),
        }
        async with client_factory(routes) as client:
            with pytest.raises(ApiError):
                await client.reply_templates_get(999)


# ───────────────── create ─────────────────


class TestReplyTemplatesCreate:
    @pytest.mark.asyncio
    async def test_create_sends_camelcase_body(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(req.content.decode())
            return success_response(_full_row(id_=101, public_id="new-uuid"))

        routes = {"POST /api/reply-templates": handler}
        async with client_factory(routes) as client:
            full = await client.reply_templates_create(
                title="hi", kind=REPLY_TEMPLATE_KIND_SINGLE,
                items=[ReplyTemplateItem(
                    position=0,
                    type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                    caption="hello",
                )],
            )
        assert captured["body"] == {
            "title": "hi",
            "kind": "single",
            "items": [{"position": 0, "type": "text", "caption": "hello"}],
        }
        assert full.id == 101 and full.public_id == "new-uuid"

    @pytest.mark.asyncio
    async def test_create_album_serializes_full_metadata(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(req.content.decode())
            return success_response(_full_row(kind="album", items=[]))

        routes = {"POST /api/reply-templates": handler}
        items_in = [
            ReplyTemplateItem(
                position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                caption="header",
                media_object_key="shared/x/0.jpg",
                mime="image/jpeg", size_bytes=1000, width=1280, height=960,
                origin_tenant_id="t1", origin_message_id="m9",
            ),
            ReplyTemplateItem(
                position=1, type=REPLY_TEMPLATE_ITEM_TYPE_VIDEO,
                media_object_key="shared/x/1.mp4",
                mime="video/mp4", size_bytes=10**6, duration_ms=15000,
                width=1920, height=1080,
            ),
            ReplyTemplateItem(
                position=2, type=REPLY_TEMPLATE_ITEM_TYPE_GIF,
                media_object_key="shared/x/2.gif",
            ),
        ]
        async with client_factory(routes) as client:
            await client.reply_templates_create(
                title="album", kind=REPLY_TEMPLATE_KIND_ALBUM, items=items_in,
            )
        body_items = captured["body"]["items"]
        assert len(body_items) == 3
        assert body_items[0]["mediaObjectKey"] == "shared/x/0.jpg"
        assert body_items[0]["originMessageId"] == "m9"
        assert body_items[1]["durationMs"] == 15000
        # None fields must NOT leak into payload
        assert "caption" not in body_items[2]
        assert "mime" not in body_items[2]


class TestReplyTemplatesCreateValidation:
    """Each case must raise ConfigError without hitting HTTP."""

    @pytest.fixture
    def no_http_routes(self):
        def must_not_call(req):
            pytest.fail(f"HTTP must not be called: {req.url.path}")
        return {
            "GET /api/reply-templates": must_not_call,
            "POST /api/reply-templates": must_not_call,
        }

    @pytest.mark.asyncio
    async def test_empty_title(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="  ", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(position=0, type="text", caption="x")],
                )

    @pytest.mark.asyncio
    async def test_unknown_kind(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind="compound",
                    items=[ReplyTemplateItem(position=0, type="text", caption="x")],
                )

    @pytest.mark.asyncio
    async def test_single_with_two_items(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[
                        ReplyTemplateItem(position=0, type="text", caption="a"),
                        ReplyTemplateItem(position=1, type="text", caption="b"),
                    ],
                )

    @pytest.mark.asyncio
    async def test_album_one_item(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[ReplyTemplateItem(
                        position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                        media_object_key="x",
                    )],
                )

    @pytest.mark.asyncio
    async def test_album_with_file(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[
                        ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="x"),
                        ReplyTemplateItem(position=1, type=REPLY_TEMPLATE_ITEM_TYPE_FILE,
                                          media_object_key="y"),
                    ],
                )

    @pytest.mark.asyncio
    async def test_album_with_voice(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[
                        ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="x"),
                        ReplyTemplateItem(position=1, type=REPLY_TEMPLATE_ITEM_TYPE_VOICE,
                                          media_object_key="y"),
                    ],
                )

    @pytest.mark.asyncio
    async def test_album_caption_on_position_1(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[
                        ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="x"),
                        ReplyTemplateItem(position=1, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="y", caption="oops"),
                    ],
                )

    @pytest.mark.asyncio
    async def test_text_with_media_key(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(
                        position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                        caption="hi", media_object_key="bad",
                    )],
                )

    @pytest.mark.asyncio
    async def test_text_missing_caption(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT)],
                )

    @pytest.mark.asyncio
    async def test_photo_without_media(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO)],
                )

    @pytest.mark.asyncio
    async def test_voice_with_caption(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(
                        position=0, type=REPLY_TEMPLATE_ITEM_TYPE_VOICE,
                        media_object_key="x", caption="no",
                    )],
                )

    @pytest.mark.asyncio
    async def test_sticker_with_caption(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(
                        position=0, type="sticker",
                        media_object_key="x", caption="no",
                    )],
                )

    @pytest.mark.asyncio
    async def test_video_note_with_caption(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(
                        position=0, type=REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE,
                        media_object_key="x", caption="no",
                    )],
                )

    @pytest.mark.asyncio
    async def test_unknown_type(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(position=0, type="screenshot",
                                              media_object_key="x")],
                )

    @pytest.mark.asyncio
    async def test_duplicate_positions(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[
                        ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="x"),
                        ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="y"),
                    ],
                )

    @pytest.mark.asyncio
    async def test_positions_not_contiguous(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[
                        ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="x"),
                        ReplyTemplateItem(position=1, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="y"),
                        ReplyTemplateItem(position=3, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key="z"),
                    ],
                )

    @pytest.mark.asyncio
    async def test_11_items_rejected(self, client_factory, no_http_routes):
        async with client_factory(no_http_routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="t", kind=REPLY_TEMPLATE_KIND_ALBUM,
                    items=[
                        ReplyTemplateItem(position=i, type=REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
                                          media_object_key=f"x{i}")
                        for i in range(11)
                    ],
                )


# ───────────────── delete ─────────────────


class TestReplyTemplatesDelete:
    @pytest.mark.asyncio
    async def test_delete_maps_response(self, client_factory):
        routes = {
            "DELETE /api/reply-templates/{template_id}":
                lambda req: success_response({"id": 42, "publicId": "uuid-42"}),
        }
        async with client_factory(routes) as client:
            res = await client.reply_templates_delete(42)
        assert res.id == 42 and res.public_id == "uuid-42"

    @pytest.mark.asyncio
    async def test_delete_validates_id(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_delete(0)
            with pytest.raises(ConfigError):
                await client.reply_templates_delete(-1)

    @pytest.mark.asyncio
    async def test_delete_403_surfaces_as_auth_error(self, client_factory):
        routes = {
            "DELETE /api/reply-templates/{template_id}":
                lambda req: error_response(
                    "Only the creator may delete this template", status=403,
                ),
        }
        async with client_factory(routes) as client:
            with pytest.raises(AuthError):
                await client.reply_templates_delete(42)

    @pytest.mark.asyncio
    async def test_delete_404_surfaces_as_api_error(self, client_factory):
        routes = {
            "DELETE /api/reply-templates/{template_id}":
                lambda req: error_response("Reply template not found", status=404),
        }
        async with client_factory(routes) as client:
            with pytest.raises(ApiError):
                await client.reply_templates_delete(999)
