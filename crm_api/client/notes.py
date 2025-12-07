from __future__ import annotations

from typing import List

from ..models import NoteItem, NoteStaff
from ..utils import parse_dt


class NotesAPI:
    # --------------- Notes ---------------

    async def list_user_notes(self, user_id: int) -> List[NoteItem]:
        d = await self._get(f"/api/users/{user_id}/notes", params=None, need_auth=True)
        items: List[NoteItem] = []
        for n in d or []:
            staff = n.get("staff") or {}
            items.append(
                NoteItem(
                    staff=NoteStaff(id=staff.get("id"), name=staff.get("name")),
                    date=parse_dt(n.get("date")),
                    text=n.get("text") or "",
                )
            )
        return items

    async def create_user_note(self, user_id: int, text: str) -> NoteItem:
        payload = {"text": text}
        n = await self._post(f"/api/users/{user_id}/notes", payload, need_auth=True)
        staff = n.get("staff") or {}
        return NoteItem(
            staff=NoteStaff(id=staff.get("id"), name=staff.get("name")),
            date=parse_dt(n.get("date")),
            text=n.get("text") or "",
        )

