from __future__ import annotations

from typing import List

from ..models import StaffInfo, StaffListItem


class StaffAPI:
    # --------------- Staff ---------------

    async def get_staff(self) -> StaffInfo:
        d = await self._get("/api/staff", params=None, need_auth=True)
        return StaffInfo(
            name=d.get("name"),
            role=d.get("role"),
            is_active=bool(d.get("is_active")),
            access=d.get("access"),
        )

    async def list_staff(self) -> List[StaffListItem]:
        """GET /api/staff/list — короткая инфа обо всех сотрудниках с user_id > 1000."""
        data = await self._get("/api/staff/list", params=None, need_auth=True)
        items: List[StaffListItem] = []
        for d in data or []:
            items.append(StaffListItem(user_id=int(d["user_id"]), name=str(d["name"]), role=str(d["role"])))
        return items

