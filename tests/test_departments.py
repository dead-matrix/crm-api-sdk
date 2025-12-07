"""Tests for DepartmentsAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestDepartmentsAPI:
    @pytest.mark.asyncio
    async def test_list_departments_success(self, client_factory):
        """Test list_departments returns properly mapped DepartmentItem list."""
        mock_data = [
            {"id": 1, "name": "support", "title": "Техподдержка"},
            {"id": 2, "name": "sales", "title": "Продажи"},
            {"id": 3, "name": "billing", "title": "Биллинг"},
        ]
        routes = {
            "GET /api/departments": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.list_departments()
            
            assert len(result) == 3
            
            assert result[0].id == 1
            assert result[0].name == "support"
            assert result[0].title == "Техподдержка"
            
            assert result[1].id == 2
            assert result[1].name == "sales"
            assert result[1].title == "Продажи"
            
            assert result[2].id == 3
            assert result[2].name == "billing"
            assert result[2].title == "Биллинг"

    @pytest.mark.asyncio
    async def test_list_departments_empty(self, client_factory):
        """Test list_departments with empty response."""
        routes = {
            "GET /api/departments": lambda req: success_response([]),
        }
        async with client_factory(routes) as client:
            result = await client.list_departments()
            assert result == []

    @pytest.mark.asyncio
    async def test_list_departments_single(self, client_factory):
        """Test list_departments with single department."""
        mock_data = [
            {"id": 99, "name": "only_one", "title": "Единственный отдел"},
        ]
        routes = {
            "GET /api/departments": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.list_departments()
            
            assert len(result) == 1
            assert result[0].id == 99
            assert result[0].name == "only_one"
            assert result[0].title == "Единственный отдел"

