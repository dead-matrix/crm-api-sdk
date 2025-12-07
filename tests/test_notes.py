"""Tests for NotesAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestNotesAPI:
    @pytest.mark.asyncio
    async def test_list_user_notes_success(self, client_factory):
        """Test list_user_notes returns properly mapped NoteItem list."""
        mock_data = [
            {
                "staff": {"id": 1, "name": "Admin"},
                "date": "2024-01-15T10:30:00+00:00",
                "text": "First note about user",
            },
            {
                "staff": {"id": 2, "name": "Support"},
                "date": "2024-01-16T14:00:00+00:00",
                "text": "Follow-up note",
            },
        ]
        routes = {
            "GET /api/users/{user_id}/notes": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.list_user_notes(user_id=123)
            
            assert len(result) == 2
            
            note1 = result[0]
            assert note1.staff.id == 1
            assert note1.staff.name == "Admin"
            assert note1.text == "First note about user"
            assert note1.date is not None
            
            note2 = result[1]
            assert note2.staff.id == 2
            assert note2.staff.name == "Support"
            assert note2.text == "Follow-up note"

    @pytest.mark.asyncio
    async def test_list_user_notes_empty(self, client_factory):
        """Test list_user_notes with empty response."""
        routes = {
            "GET /api/users/{user_id}/notes": lambda req: success_response([]),
        }
        async with client_factory(routes) as client:
            result = await client.list_user_notes(user_id=123)
            assert result == []

    @pytest.mark.asyncio
    async def test_list_user_notes_missing_staff(self, client_factory):
        """Test list_user_notes handles missing staff gracefully."""
        mock_data = [
            {
                "date": "2024-01-15T10:30:00Z",
                "text": "Note without staff info",
            },
        ]
        routes = {
            "GET /api/users/{user_id}/notes": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.list_user_notes(user_id=123)
            
            assert len(result) == 1
            assert result[0].staff.id is None
            assert result[0].staff.name is None
            assert result[0].text == "Note without staff info"

    @pytest.mark.asyncio
    async def test_create_user_note_success(self, client_factory):
        """Test create_user_note returns created NoteItem."""
        mock_data = {
            "staff": {"id": 1, "name": "Admin"},
            "date": "2024-01-20T12:00:00+00:00",
            "text": "New note created",
        }
        routes = {
            "POST /api/users/{user_id}/notes": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.create_user_note(user_id=123, text="New note created")
            
            assert result.staff.id == 1
            assert result.staff.name == "Admin"
            assert result.text == "New note created"
            assert result.date is not None

    @pytest.mark.asyncio
    async def test_create_user_note_empty_text_response(self, client_factory):
        """Test create_user_note handles empty text in response."""
        mock_data = {
            "staff": {"id": 1, "name": "Admin"},
            "date": "2024-01-20T12:00:00Z",
            # text is missing
        }
        routes = {
            "POST /api/users/{user_id}/notes": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.create_user_note(user_id=123, text="Some text")
            assert result.text == ""  # defaults to empty string

