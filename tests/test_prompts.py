"""Tests for PromptsAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestPromptsAPI:
    @pytest.mark.asyncio
    async def test_prompt_get_success(self, client_factory):
        """Test prompt_get returns prompt string."""
        mock_data = "Ты — помощник по продажам. Отвечай вежливо и по делу."
        routes = {
            "GET /api/prompt": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.prompt_get(user_id=123)
            assert result == "Ты — помощник по продажам. Отвечай вежливо и по делу."

    @pytest.mark.asyncio
    async def test_prompt_get_empty(self, client_factory):
        """Test prompt_get returns None when no prompt set."""
        routes = {
            "GET /api/prompt": lambda req: success_response(None),
        }
        async with client_factory(routes) as client:
            result = await client.prompt_get(user_id=123)
            assert result is None

    @pytest.mark.asyncio
    async def test_prompt_update_success(self, client_factory):
        """Test prompt_update returns PromptUpdateResult."""
        mock_data = {
            "reset": False,
            "message": "Prompt updated successfully",
            "updated": True,
            "created": False,
        }
        routes = {
            "POST /api/prompt/update": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.prompt_update(user_id=123, prompt="New prompt text")
            
            assert result.reset is False
            assert result.message == "Prompt updated successfully"
            assert result.updated is True
            assert result.created is False

    @pytest.mark.asyncio
    async def test_prompt_update_created(self, client_factory):
        """Test prompt_update when creating new prompt."""
        mock_data = {
            "reset": False,
            "message": "Prompt created",
            "updated": False,
            "created": True,
        }
        routes = {
            "POST /api/prompt/update": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.prompt_update(user_id=123, prompt="First prompt")
            
            assert result.created is True
            assert result.updated is False

    @pytest.mark.asyncio
    async def test_prompt_update_reset(self, client_factory):
        """Test prompt_update with reset."""
        mock_data = {
            "reset": True,
            "message": "Prompt reset to default",
            "updated": False,
            "created": False,
        }
        routes = {
            "POST /api/prompt/update": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.prompt_update(user_id=123, prompt="")
            
            assert result.reset is True
            assert result.message == "Prompt reset to default"

