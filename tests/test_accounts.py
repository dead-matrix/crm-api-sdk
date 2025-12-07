"""Tests for AccountsAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response, error_response


class TestAccountsAPI:
    @pytest.mark.asyncio
    async def test_accounts_list_success(self, client_factory):
        """Test accounts_list returns properly mapped AccountItem list."""
        mock_data = [
            {
                "session_name": "session1",
                "valid": True,
                "spam_block": False,
                "is_connected": True,
                "location": "RU",
                "full_name": "Test User",
                "username": "testuser",
                "phone": "+79001234567",
                "premium": True,
                "commented": {"day": 10, "total": 100},
                "invited": {"day": 5, "total": 50},
                "stories": {"day": 2, "total": 20},
                "tagged": {"day": 1, "total": 10},
                "views": {"day": 100, "total": 1000},
                "reactions": {"day": 15, "total": 150},
            }
        ]
        routes = {
            "GET /api/accounts/list": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.accounts_list(user_id=123)
            
            assert len(result) == 1
            acc = result[0]
            assert acc.session_name == "session1"
            assert acc.valid is True
            assert acc.spam_block is False
            assert acc.is_connected is True
            assert acc.location == "RU"
            assert acc.full_name == "Test User"
            assert acc.username == "testuser"
            assert acc.phone == "+79001234567"
            assert acc.premium is True
            assert acc.commented.day == 10
            assert acc.commented.total == 100
            assert acc.invited.day == 5
            assert acc.invited.total == 50
            assert acc.stories.day == 2
            assert acc.stories.total == 20
            assert acc.tagged.day == 1
            assert acc.tagged.total == 10
            assert acc.views.day == 100
            assert acc.views.total == 1000
            assert acc.reactions.day == 15
            assert acc.reactions.total == 150

    @pytest.mark.asyncio
    async def test_accounts_list_empty(self, client_factory):
        """Test accounts_list with empty response."""
        routes = {
            "GET /api/accounts/list": lambda req: success_response([]),
        }
        async with client_factory(routes) as client:
            result = await client.accounts_list(user_id=123)
            assert result == []

    @pytest.mark.asyncio
    async def test_accounts_list_invalid_user_id(self, client_factory):
        """Test accounts_list raises ConfigError for invalid user_id."""
        from crm_api.exceptions import ConfigError
        
        routes = {}
        async with client_factory(routes) as client:
            with pytest.raises(ConfigError, match="user_id must be positive"):
                await client.accounts_list(user_id=0)
            with pytest.raises(ConfigError, match="user_id must be positive"):
                await client.accounts_list(user_id=-1)

    @pytest.mark.asyncio
    async def test_accounts_list_partial_data(self, client_factory):
        """Test accounts_list handles missing optional fields gracefully."""
        mock_data = [
            {
                "session_name": "session2",
                "valid": False,
                # Missing most fields - should default gracefully
            }
        ]
        routes = {
            "GET /api/accounts/list": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.accounts_list(user_id=123)
            
            assert len(result) == 1
            acc = result[0]
            assert acc.session_name == "session2"
            assert acc.valid is False
            assert acc.spam_block is False
            assert acc.is_connected is False
            assert acc.commented.day == 0
            assert acc.commented.total == 0

