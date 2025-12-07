"""Tests for TasksAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestTasksAPI:
    @pytest.mark.asyncio
    async def test_tasks_types_success(self, client_factory):
        """Test tasks_types returns dict of task types."""
        mock_data = {
            "masslooking": "Масслукинг",
            "inviting": "Инвайтинг",
            "commenting": "Комментинг",
        }
        routes = {
            "GET /api/tasks/types": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.tasks_types(user_id=123, bot_id=1)
            
            assert result == {
                "masslooking": "Масслукинг",
                "inviting": "Инвайтинг",
                "commenting": "Комментинг",
            }

    @pytest.mark.asyncio
    async def test_tasks_types_empty(self, client_factory):
        """Test tasks_types with empty response."""
        routes = {
            "GET /api/tasks/types": lambda req: success_response({}),
        }
        async with client_factory(routes) as client:
            result = await client.tasks_types(user_id=123, bot_id=1)
            assert result == {}

    @pytest.mark.asyncio
    async def test_tasks_list_success(self, client_factory):
        """Test tasks_list returns list of TaskListItem."""
        mock_data = [
            {"id": 1, "text": "Task 1 description"},
            {"id": 2, "text": "Task 2 description"},
            {"id": 3, "text": "Task 3 description"},
        ]
        routes = {
            "GET /api/tasks/list": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.tasks_list(
                user_id=123, bot_id=1, task_type="masslooking", limit=10, offset=0
            )
            
            assert len(result) == 3
            assert result[0].id == 1
            assert result[0].text == "Task 1 description"
            assert result[1].id == 2
            assert result[2].id == 3

    @pytest.mark.asyncio
    async def test_tasks_list_with_offset(self, client_factory):
        """Test tasks_list with offset parameter."""
        mock_data = [{"id": 11, "text": "Task 11"}]
        
        def check_params(req: httpx.Request) -> httpx.Response:
            assert req.url.params.get("offset") == "10"
            assert req.url.params.get("limit") == "5"
            return success_response(mock_data)
        
        routes = {
            "GET /api/tasks/list": check_params,
        }
        async with client_factory(routes) as client:
            result = await client.tasks_list(
                user_id=123, bot_id=1, task_type=None, limit=5, offset=10
            )
            assert len(result) == 1
            assert result[0].id == 11

    @pytest.mark.asyncio
    async def test_tasks_list_empty(self, client_factory):
        """Test tasks_list with empty response."""
        routes = {
            "GET /api/tasks/list": lambda req: success_response([]),
        }
        async with client_factory(routes) as client:
            result = await client.tasks_list(
                user_id=123, bot_id=1, task_type="inviting", limit=10
            )
            assert result == []

    @pytest.mark.asyncio
    async def test_tasks_info_success(self, client_factory):
        """Test tasks_info returns TaskInfoResult."""
        mock_data = {"text": "Detailed task information here"}
        routes = {
            "GET /api/tasks/info": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.tasks_info(
                user_id=123, bot_id=1, task_type="masslooking", task_id=42
            )
            assert result.text == "Detailed task information here"

    @pytest.mark.asyncio
    async def test_tasks_info_empty_text(self, client_factory):
        """Test tasks_info with empty text."""
        mock_data = {}
        routes = {
            "GET /api/tasks/info": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.tasks_info(
                user_id=123, bot_id=1, task_type="inviting", task_id=1
            )
            assert result.text == ""

    @pytest.mark.asyncio
    async def test_tasks_log_success(self, client_factory):
        """Test tasks_log returns filename and content bytes."""
        log_content = b"2024-01-15 10:00:00 Task started\n2024-01-15 10:05:00 Task completed\n"
        
        def file_handler(req: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                content=log_content,
                headers={"Content-Disposition": 'attachment; filename="task_42.log"'},
            )
        
        routes = {
            "GET /api/tasks/log": file_handler,
        }
        async with client_factory(routes) as client:
            filename, content = await client.tasks_log(
                user_id=123, task_type="masslooking", task_id=42, bot_id=1
            )
            
            assert filename == "task_42.log"
            assert content == log_content

    @pytest.mark.asyncio
    async def test_tasks_log_utf8_filename(self, client_factory):
        """Test tasks_log with UTF-8 encoded filename."""
        log_content = b"Log data"
        
        def file_handler(req: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                content=log_content,
                headers={"Content-Disposition": "attachment; filename*=UTF-8''%D0%BB%D0%BE%D0%B3.txt"},
            )
        
        routes = {
            "GET /api/tasks/log": file_handler,
        }
        async with client_factory(routes) as client:
            filename, content = await client.tasks_log(
                user_id=123, task_type="inviting", task_id=1, bot_id=1
            )
            
            assert filename == "%D0%BB%D0%BE%D0%B3.txt"  # URL-encoded Cyrillic
            assert content == log_content

