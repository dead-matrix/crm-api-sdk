from __future__ import annotations

from typing import List, Optional

from ..exceptions import ConfigError
from ..models import (
    DialogItem,
    StatusItem,
    StatusesResult,
    ChangeStatusResult,
    TransferDialogResult,
    DialogSearchItem,
    DialogSearchResult,
)


class DialogsAPI:
    # --------------- Dialogs ---------------

    async def get_dialogs(self, department: str) -> List[DialogItem]:
        d = await self._get(f"/api/dialogs/{department}", params=None, need_auth=True)
        items: List[DialogItem] = []
        for r in d.get("dialogs") or []:
            items.append(
                DialogItem(
                    user_id=int(r["user_id"]),
                    full_name=r.get("full_name"),
                    has_active_subscription=bool(r.get("has_active_subscription")),
                    status=r.get("status"),
                    status_color=r.get("status_color"),
                )
            )
        return items

    async def get_statuses(self, department_id: int) -> StatusesResult:
        if department_id <= 0:
            raise ConfigError("department_id must be positive integer")
        d = await self._get(f"/api/dialogs/statuses/{department_id}", params=None, need_auth=True)
        statuses: List[StatusItem] = []
        for s in d.get("statuses") or []:
            statuses.append(StatusItem(id=int(s["id"]), title=str(s["title"]), color=s.get("color")))
        return StatusesResult(
            department_id=int(d["department_id"]),
            default_status_id=d.get("default_status_id"),
            statuses=statuses,
        )

    async def change_dialog_status(self, user_id: int, status_id: int) -> ChangeStatusResult:
        if user_id <= 0:
            raise ConfigError("user_id must be positive integer")
        if status_id <= 0:
            raise ConfigError("status_id must be positive integer")
        payload = {"user_id": int(user_id), "status_id": int(status_id)}
        d = await self._post("/api/dialogs/status", payload, need_auth=True)
        return ChangeStatusResult(status=str(d.get("status")))

    async def transfer_dialog(self, user_id: int, to_department: str) -> TransferDialogResult:
        payload = {"user_id": int(user_id), "to_department": str(to_department)}
        d = await self._post("/api/dialogs/transfer", payload, need_auth=True)
        return TransferDialogResult(transferred=bool(d.get("transferred")))

    async def search_dialogs(
        self, department: str, q: str, offset: int = 0
    ) -> DialogSearchResult:
        """
        GET /api/dialogs/{department}/search — поиск диалогов по строке.

        Ищет совпадения в user_id, full_name и username.

        Args:
            department: Название отдела (например: "sales")
            q: Поисковый запрос (1-256 символов)
            offset: Смещение для пагинации (>= 0, по умолчанию 0)

        Returns:
            DialogSearchResult с найденными диалогами и информацией о пагинации
        """
        if not q or not q.strip():
            raise ConfigError("q (search query) must not be empty")
        if offset < 0:
            raise ConfigError("offset must be non-negative integer")

        params = {"q": str(q), "offset": int(offset)}
        d = await self._get(f"/api/dialogs/{department}/search", params=params, need_auth=True)

        dialogs: List[DialogSearchItem] = []
        for r in d.get("dialogs") or []:
            dialogs.append(
                DialogSearchItem(
                    user_id=int(r["user_id"]),
                    full_name=r.get("full_name"),
                    has_active_subscription=bool(r.get("has_active_subscription")),
                    status=str(r.get("status", "")),
                    status_color=str(r.get("status_color", "")),
                )
            )

        return DialogSearchResult(
            dialogs=dialogs,
            limit=int(d.get("limit", 50)),
            offset=int(d.get("offset", 0)),
        )

