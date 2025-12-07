from __future__ import annotations

from typing import List

from ..models import DepartmentItem


class DepartmentsAPI:
    # --------------- Departments ---------------

    async def list_departments(self) -> List[DepartmentItem]:
        data = await self._get("/api/departments", params=None, need_auth=True)
        items: List[DepartmentItem] = []
        for d in data or []:
            items.append(DepartmentItem(id=int(d["id"]), name=str(d["name"]), title=str(d["title"])))
        return items

