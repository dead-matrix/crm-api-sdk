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


# ───────────────── public_id (Phase 3) ─────────────────


class TestReplyTemplatesPublicID:
    @pytest.mark.asyncio
    async def test_create_round_trips_public_id_lowercased(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(req.content.decode())
            return success_response(_full_row(id_=200, public_id="01234567-89ab-cdef-0123-456789abcdef"))

        routes = {"POST /api/reply-templates": handler}
        async with client_factory(routes) as client:
            full = await client.reply_templates_create(
                title="x", kind=REPLY_TEMPLATE_KIND_SINGLE,
                items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                                          caption="hi")],
                public_id="01234567-89AB-CDEF-0123-456789ABCDEF",
            )
        assert captured["body"]["publicId"] == "01234567-89ab-cdef-0123-456789abcdef"
        assert full.public_id == "01234567-89ab-cdef-0123-456789abcdef"

    @pytest.mark.asyncio
    async def test_create_omits_public_id_when_none(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(req.content.decode())
            return success_response(_full_row())

        routes = {"POST /api/reply-templates": handler}
        async with client_factory(routes) as client:
            await client.reply_templates_create(
                title="x", kind=REPLY_TEMPLATE_KIND_SINGLE,
                items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                                          caption="hi")],
            )
        assert "publicId" not in captured["body"]

    @pytest.mark.asyncio
    async def test_create_omits_public_id_when_empty_string(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(req.content.decode())
            return success_response(_full_row())

        routes = {"POST /api/reply-templates": handler}
        async with client_factory(routes) as client:
            await client.reply_templates_create(
                title="x", kind=REPLY_TEMPLATE_KIND_SINGLE,
                items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                                          caption="hi")],
                public_id="",
            )
        assert "publicId" not in captured["body"]

    @pytest.mark.parametrize(
        "bad",
        [
            "not-a-uuid",
            "01234567-89ab-cdef-0123-456789abcde",
            "0123456789abcdef0123456789abcdef",
        ],
    )
    @pytest.mark.asyncio
    async def test_create_bad_public_id_rejected_before_http(self, client_factory, bad):
        def must_not_call(req):
            pytest.fail(f"HTTP must not be called: {req.url.path}")

        routes = {"POST /api/reply-templates": must_not_call}
        async with client_factory(routes) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_create(
                    title="x", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                                              caption="hi")],
                    public_id=bad,
                )

    @pytest.mark.asyncio
    async def test_create_duplicate_409_surfaces_as_api_error(self, client_factory):
        routes = {
            "POST /api/reply-templates":
                lambda req: error_response("public_id already exists", status=409),
        }
        async with client_factory(routes) as client:
            with pytest.raises(ApiError):
                await client.reply_templates_create(
                    title="x", kind=REPLY_TEMPLATE_KIND_SINGLE,
                    items=[ReplyTemplateItem(position=0, type=REPLY_TEMPLATE_ITEM_TYPE_TEXT,
                                              caption="hi")],
                    public_id="01234567-89ab-cdef-0123-456789abcdef",
                )


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


# ─────────── item id surfacing ───────────


class TestReplyTemplateItemId:
    """Read-response items[] must carry the per-row id. The messenger
    keys delivery-ref upserts by it; if the SDK silently drops it,
    cache writes will all collide on item_id=0."""

    @pytest.mark.asyncio
    async def test_get_propagates_item_ids(self, client_factory):
        items = [
            {"id": 100, "position": 0, "type": "photo",
             "mediaObjectKey": "shared/reply-templates/uuid-1/0.jpg"},
            {"id": 101, "position": 1, "type": "video",
             "mediaObjectKey": "shared/reply-templates/uuid-1/1.mp4"},
        ]
        routes = {
            "GET /api/reply-templates/{template_id}":
                lambda req: success_response(_full_row(id_=1, items=items)),
        }
        async with client_factory(routes) as client:
            full = await client.reply_templates_get(1)
        assert [it.id for it in full.items] == [100, 101]


# ─────────── delivery refs ───────────


class TestReplyTemplatesDeliveryRefsList:
    @pytest.mark.asyncio
    async def test_empty(self, client_factory):
        routes = {
            "GET /api/reply-templates/{template_id}/delivery-refs":
                lambda req: success_response({"refs": []}),
        }
        async with client_factory(routes) as client:
            refs = await client.reply_templates_delivery_refs_list(
                42, provider="telegram", provider_scope="tg_bot",
            )
        assert refs == []

    @pytest.mark.asyncio
    async def test_maps_rows(self, client_factory):
        routes = {
            "GET /api/reply-templates/{template_id}/delivery-refs":
                lambda req: success_response({"refs": [
                    {
                        "id": 1, "itemId": 10, "provider": "telegram",
                        "providerScope": "tg_bot",
                        "mediaRef": "BAACAg-photo-id",
                        "mediaUniqueRef": "AgADxx", "mediaType": "photo",
                        "failCount": 0,
                        "lastUsedAt": "2026-05-18T12:00:00",
                        "createdAt": "2026-05-18T11:00:00",
                        "updatedAt": "2026-05-18T12:00:00",
                    },
                    {
                        "id": 2, "itemId": 11, "provider": "telegram",
                        "providerScope": "tg_bot",
                        "mediaRef": "BAACAg-video-id",
                        "mediaUniqueRef": None, "mediaType": "video",
                        "failCount": 1,
                        "lastUsedAt": None, "createdAt": None, "updatedAt": None,
                    },
                ]}),
        }
        async with client_factory(routes) as client:
            refs = await client.reply_templates_delivery_refs_list(
                9, provider="telegram", provider_scope="tg_bot",
            )
        assert len(refs) == 2
        assert (refs[0].item_id, refs[0].media_ref) == (10, "BAACAg-photo-id")
        assert refs[0].fail_count == 0
        assert refs[1].media_unique_ref is None
        assert refs[1].fail_count == 1

    @pytest.mark.asyncio
    async def test_sends_query_params(self, client_factory):
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["query"] = dict(req.url.params)
            return success_response({"refs": []})

        routes = {"GET /api/reply-templates/{template_id}/delivery-refs": handler}
        async with client_factory(routes) as client:
            await client.reply_templates_delivery_refs_list(
                7, provider="telegram", provider_scope="tg_crm_bot",
            )
        assert captured["query"] == {
            "provider": "telegram",
            "providerScope": "tg_crm_bot",
        }

    @pytest.mark.asyncio
    async def test_validates_args(self, client_factory):
        async with client_factory({}) as client:
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_list(
                    0, provider="telegram", provider_scope="x",
                )
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_list(
                    1, provider="", provider_scope="x",
                )
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_list(
                    1, provider="telegram", provider_scope="   ",
                )


class TestReplyTemplatesDeliveryRefsUpsert:
    @pytest.mark.asyncio
    async def test_sends_camel_case_payload(self, client_factory):
        from crm_api.models import UpsertDeliveryRefInput, UpsertDeliveryRefsInput
        captured: Dict[str, Any] = {}

        def handler(req: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(req.content.decode())
            captured["method"] = req.method
            return success_response({"refs": [
                {
                    "id": 1, "itemId": 11, "provider": "telegram",
                    "providerScope": "tg_bot", "mediaRef": "BAA",
                    "mediaUniqueRef": None, "mediaType": "photo",
                    "failCount": 0,
                    "lastUsedAt": None, "createdAt": None, "updatedAt": None,
                },
            ]})

        routes = {"PUT /api/reply-templates/{template_id}/delivery-refs": handler}
        async with client_factory(routes) as client:
            refs = await client.reply_templates_delivery_refs_upsert(
                5,
                UpsertDeliveryRefsInput(
                    provider="telegram",
                    provider_scope="tg_bot",
                    refs=[UpsertDeliveryRefInput(item_id=11, media_ref="BAA", media_type="photo")],
                ),
            )

        assert captured["method"] == "PUT"
        assert captured["body"]["provider"] == "telegram"
        assert captured["body"]["providerScope"] == "tg_bot"
        assert captured["body"]["refs"][0]["itemId"] == 11
        assert captured["body"]["refs"][0]["mediaRef"] == "BAA"
        assert refs[0].item_id == 11
        assert refs[0].fail_count == 0

    @pytest.mark.asyncio
    async def test_validates_payload_before_http(self, client_factory):
        from crm_api.models import UpsertDeliveryRefInput, UpsertDeliveryRefsInput

        def must_not_call(req):
            pytest.fail(f"HTTP must not be called: {req.url.path}")

        routes = {"PUT /api/reply-templates/{template_id}/delivery-refs": must_not_call}
        async with client_factory(routes) as client:
            # Empty refs
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_upsert(
                    1, UpsertDeliveryRefsInput(provider="telegram", provider_scope="x", refs=[]),
                )
            # Empty provider
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_upsert(
                    1, UpsertDeliveryRefsInput(provider="", provider_scope="x",
                                               refs=[UpsertDeliveryRefInput(item_id=1, media_ref="ok")]),
                )
            # Empty media_ref
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_upsert(
                    1, UpsertDeliveryRefsInput(provider="telegram", provider_scope="x",
                                               refs=[UpsertDeliveryRefInput(item_id=1, media_ref=" ")]),
                )
            # Too many refs (>10)
            with pytest.raises(ConfigError):
                await client.reply_templates_delivery_refs_upsert(
                    1,
                    UpsertDeliveryRefsInput(
                        provider="telegram", provider_scope="x",
                        refs=[
                            UpsertDeliveryRefInput(item_id=i + 1, media_ref="ok")
                            for i in range(11)
                        ],
                    ),
                )

    @pytest.mark.asyncio
    async def test_422_surfaces_as_validation_error(self, client_factory):
        """The SDK's HTTP layer maps 4xx-with-VALIDATION_ERROR code (or
        422) to ValidationError, not generic ApiError. Cross-template
        item-id rejection lands here, so callers can distinguish 'bad
        input, fix the args' from 'transient server error'."""
        from crm_api.exceptions import ValidationError
        from crm_api.models import UpsertDeliveryRefInput, UpsertDeliveryRefsInput

        routes = {
            "PUT /api/reply-templates/{template_id}/delivery-refs":
                lambda req: error_response(
                    "item ids do not belong to template 5", status=422,
                ),
        }
        async with client_factory(routes) as client:
            with pytest.raises(ValidationError):
                await client.reply_templates_delivery_refs_upsert(
                    5,
                    UpsertDeliveryRefsInput(
                        provider="telegram", provider_scope="x",
                        refs=[UpsertDeliveryRefInput(item_id=99, media_ref="BAA")],
                    ),
                )
