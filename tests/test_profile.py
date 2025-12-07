"""Tests for ProfileAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestProfileAPI:
    @pytest.mark.asyncio
    async def test_profile_statistics_success(self, client_factory):
        """Test profile_statistics returns ProfileStatistics."""
        mock_data = {
            "subscriber": True,
            "all_accounts_amount": 5,
            "all_invited": 100,
            "all_commented": 200,
            "all_stories": 50,
            "all_tagged": 30,
            "all_views": 1000,
            "all_reactions": 150,
            "tasks": 10,
            "valid": 4,
            "work": 3,
            "invalid": 1,
            "spam_block": 0,
            "invited": 20,
            "commented": 40,
            "stories": 10,
            "tagged": 5,
            "views": 200,
            "reactions": 30,
            "quota": {"daily": 100, "used": 50},
        }
        routes = {
            "GET /api/profile/statistics": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.profile_statistics(user_id=123)
            
            assert result.subscriber is True
            assert result.all_accounts_amount == 5
            assert result.all_invited == 100
            assert result.all_commented == 200
            assert result.all_stories == 50
            assert result.all_tagged == 30
            assert result.all_views == 1000
            assert result.all_reactions == 150
            assert result.tasks == 10
            assert result.valid == 4
            assert result.work == 3
            assert result.invalid == 1
            assert result.spam_block == 0
            assert result.invited == 20
            assert result.commented == 40
            assert result.stories == 10
            assert result.tagged == 5
            assert result.views == 200
            assert result.reactions == 30
            assert result.quota == {"daily": 100, "used": 50}

    @pytest.mark.asyncio
    async def test_profile_statistics_minimal(self, client_factory):
        """Test profile_statistics with minimal data."""
        mock_data = {"subscriber": False}
        routes = {
            "GET /api/profile/statistics": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.profile_statistics(user_id=123)
            
            assert result.subscriber is False
            assert result.all_accounts_amount == 0
            assert result.quota is None

    @pytest.mark.asyncio
    async def test_profile_bot3_summary_success(self, client_factory):
        """Test profile_bot3_summary returns Bot3Summary."""
        mock_data = {
            "subscription": {
                "active": True,
                "access": "premium",
                "access_end": "2025-01-01T00:00:00+00:00",
            },
            "account": {
                "telegram_id": 123456789,
                "valid": True,
                "is_connected": True,
                "last_connection": "2024-12-01T10:00:00+00:00",
                "premium": True,
                "full_name": "Test User",
                "username": "testuser",
                "location": "RU",
            },
            "tasks": {"pending": 5, "completed": 10},
        }
        routes = {
            "GET /api/profile/bot3/summary": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.profile_bot3_summary(user_id=123)
            
            assert result.subscription.active is True
            assert result.subscription.access == "premium"
            assert result.subscription.access_end is not None
            
            assert result.account is not None
            assert result.account.telegram_id == 123456789
            assert result.account.valid is True
            assert result.account.is_connected is True
            assert result.account.premium is True
            assert result.account.full_name == "Test User"
            assert result.account.username == "testuser"
            assert result.account.location == "RU"
            
            assert result.tasks == {"pending": 5, "completed": 10}

    @pytest.mark.asyncio
    async def test_profile_bot3_summary_no_account(self, client_factory):
        """Test profile_bot3_summary without account."""
        mock_data = {
            "subscription": {
                "active": False,
                "access": None,
                "access_end": None,
            },
            "account": None,
            "tasks": {},
        }
        routes = {
            "GET /api/profile/bot3/summary": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.profile_bot3_summary(user_id=123)
            
            assert result.subscription.active is False
            assert result.account is None
            assert result.tasks == {}

