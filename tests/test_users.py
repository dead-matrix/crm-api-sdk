from __future__ import annotations

import asyncio
import sys
import pathlib
from typing import Any, Dict

import httpx
import pytest

# Ensure repo root on path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from crm_api.client import CRMApiClient
from crm_api.models import CreateUserInput, UpdateUserInput


def make_handler() -> httpx.MockTransport:
    state: Dict[str, Any] = {
        "auth_calls": 0,
        "users_get_calls": 0,
    }

    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        # Auth issuance
        if path.startswith("/api/staff/") and path.endswith("/auth") and req.method == "POST":
            state["auth_calls"] += 1
            data = {
                "token": f"JWT{state['auth_calls']}",
                "expires_at": "2030-01-01T00:00:00+00:00",
            }
            return httpx.Response(200, json={"status": "success", "data": data})

        # Users endpoints
        if path == "/api/users" and req.method == "POST":
            return httpx.Response(200, json={"status": "success", "data": {"created": True}})

        if path.startswith("/api/users/") and req.method == "PUT":
            import json
            user_id = int(path.split("/")[-1])
            body = json.loads(req.content.decode("utf-8"))
            data = {"user_id": user_id, "full_name": body.get("full_name"), "username": body.get("username")}
            return httpx.Response(200, json={"status": "success", "data": data})

        if path.startswith("/api/users/") and req.method == "GET":
            state["users_get_calls"] += 1
            # Force a single 401 to verify JWT refresh logic
            if state["users_get_calls"] == 1:
                return httpx.Response(401, json={"status": "error", "message": "unauthorized"})
            user_id = int(path.split("/")[-1])
            data = {
                "user_id": user_id,
                "full_name": "John Doe",
                "username": "johndoe",
                "status": "active",
                "bots_info": [
                    {
                        "bot_id": 1,
                        "bot_name": "MainBot",
                        "registered": "2024-10-01T00:00:00+00:00",
                        "refer": None,
                        "access": None,
                        "access_end": None,
                    }
                ],
            }
            return httpx.Response(200, json={"status": "success", "data": data})

        return httpx.Response(404, json={"status": "error", "message": f"not found: {path}"})

    return httpx.MockTransport(handler)


class TestUsers:
    @pytest.mark.asyncio
    async def test_users_crud_and_auth_refresh(self):
        transport = make_handler()
        async with CRMApiClient(base_url="https://example", staff_id=123, service_token="T", transport=transport) as c:
            # create
            created = await c.create_user(CreateUserInput(user_id=1, full_name="John", username="j", bot_id=1))
            assert created.created is True
            # update
            upd = await c.update_user(1, UpdateUserInput(full_name="John X", username="jx"))
            assert upd.user_id == 1 and upd.full_name == "John X" and upd.username == "jx"
            # get with forced 401 then refresh
            user = await c.get_user(1)
            assert user.user_id == 1
            assert user.full_name == "John Doe"
            assert user.bots_info and user.bots_info[0].bot_id == 1

