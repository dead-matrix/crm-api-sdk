from __future__ import annotations

from ..models import StaffInfo


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

