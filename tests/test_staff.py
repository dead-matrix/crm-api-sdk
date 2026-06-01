"""Tests for StaffAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestStaffAPI:
    @pytest.mark.asyncio
    async def test_get_staff_success(self, client_factory):
        """Test get_staff returns StaffInfo."""
        mock_data = {
            "name": "Admin User",
            "role": "admin",
            "is_active": True,
            "access": ["users", "payments", "dialogs"],
        }
        routes = {
            "GET /api/staff": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_staff()
            
            assert result.name == "Admin User"
            assert result.role == "admin"
            assert result.is_active is True
            assert result.access == ["users", "payments", "dialogs"]

    @pytest.mark.asyncio
    async def test_get_staff_minimal(self, client_factory):
        """Test get_staff with minimal data."""
        mock_data = {
            "name": "Support",
            "role": "support",
            "is_active": True,
        }
        routes = {
            "GET /api/staff": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_staff()
            
            assert result.name == "Support"
            assert result.role == "support"
            assert result.is_active is True
            assert result.access is None

    @pytest.mark.asyncio
    async def test_get_staff_inactive(self, client_factory):
        """Test get_staff for inactive staff."""
        mock_data = {
            "name": "Former Employee",
            "role": "support",
            "is_active": False,
            "access": [],
        }
        routes = {
            "GET /api/staff": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_staff()
            
            assert result.name == "Former Employee"
            assert result.is_active is False
            assert result.access == []

    @pytest.mark.asyncio
    async def test_get_staff_missing_fields(self, client_factory):
        """Test get_staff handles missing optional fields."""
        mock_data = {
            "is_active": True,
        }
        routes = {
            "GET /api/staff": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_staff()

            assert result.name is None
            assert result.role is None
            assert result.is_active is True
            assert result.access is None

    @pytest.mark.asyncio
    async def test_list_staff_success(self, client_factory):
        """Test list_staff returns properly mapped StaffListItem list."""
        mock_data = [
            {"user_id": 1001, "name": "Alice", "role": "admin"},
            {"user_id": 7014133383, "name": "Bob", "role": "support"},
        ]
        routes = {
            "GET /api/staff/list": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.list_staff()

            assert len(result) == 2

            assert result[0].user_id == 1001
            assert result[0].name == "Alice"
            assert result[0].role == "admin"

            assert result[1].user_id == 7014133383
            assert result[1].name == "Bob"
            assert result[1].role == "support"

    @pytest.mark.asyncio
    async def test_list_staff_empty(self, client_factory):
        """Test list_staff with empty response."""
        routes = {
            "GET /api/staff/list": lambda req: success_response([]),
        }
        async with client_factory(routes) as client:
            result = await client.list_staff()
            assert result == []

