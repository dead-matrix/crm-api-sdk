"""Tests for ServersAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestServersAPI:
    @pytest.mark.asyncio
    async def test_servers_restart_success(self, client_factory):
        """Test servers_restart returns ServerRestartResult."""
        mock_data = {"message": "Server restart initiated for user 123, bot 1"}
        routes = {
            "POST /api/servers/restart": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.servers_restart(user_id=123, bot_id=1)
            assert result.message == "Server restart initiated for user 123, bot 1"

    @pytest.mark.asyncio
    async def test_servers_restart_default_bot_id(self, client_factory):
        """Test servers_restart with default bot_id=1."""
        mock_data = {"message": "Restart OK"}
        
        def check_params(req: httpx.Request) -> httpx.Response:
            # Verify bot_id defaults to 1
            assert req.url.params.get("bot_id") == "1"
            return success_response(mock_data)
        
        routes = {
            "POST /api/servers/restart": check_params,
        }
        async with client_factory(routes) as client:
            result = await client.servers_restart(user_id=123)
            assert result.message == "Restart OK"

    @pytest.mark.asyncio
    async def test_servers_restart_custom_bot_id(self, client_factory):
        """Test servers_restart with custom bot_id."""
        mock_data = {"message": "Restart for bot 3"}
        
        def check_params(req: httpx.Request) -> httpx.Response:
            assert req.url.params.get("bot_id") == "3"
            assert req.url.params.get("user_id") == "456"
            return success_response(mock_data)
        
        routes = {
            "POST /api/servers/restart": check_params,
        }
        async with client_factory(routes) as client:
            result = await client.servers_restart(user_id=456, bot_id=3)
            assert result.message == "Restart for bot 3"

    @pytest.mark.asyncio
    async def test_servers_restart_empty_message(self, client_factory):
        """Test servers_restart with empty message."""
        mock_data = {}  # No message field
        routes = {
            "POST /api/servers/restart": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.servers_restart(user_id=123)
            assert result.message == ""  # defaults to empty string

