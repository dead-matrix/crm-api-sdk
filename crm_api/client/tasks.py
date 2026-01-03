from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..models import TaskListItem, TaskInfoResult, ActiveTasksResult
from ..utils import parse_content_disposition


class TasksAPI:
    # --------------- Tasks ---------------

    async def get_active_tasks(self, user_id: int) -> ActiveTasksResult:
        """
        GET /api/tasks/active — возвращает текстовое описание активных задач пользователя.

        Args:
            user_id: ID пользователя Telegram (>= 1)

        Returns:
            ActiveTasksResult с HTML-форматированным текстом активных задач
        """
        params = {"user_id": int(user_id)}
        d = await self._get("/api/tasks/active", params=params, need_auth=True)
        return ActiveTasksResult(text=str(d.get("text", "")))

    async def tasks_types(self, user_id: int, bot_id: int) -> Dict[str, str]:
        d = await self._get(
            "/api/tasks/types",
            params={"user_id": int(user_id), "bot_id": int(bot_id)},
            need_auth=True,
        )
        return {str(k): str(v) for k, v in (d or {}).items()}

    async def tasks_list(
        self,
        user_id: int,
        bot_id: int,
        task_type: Optional[str],
        limit: int,
        offset: int = 0,
    ) -> List[TaskListItem]:
        params: Dict[str, Any] = {
            "user_id": int(user_id),
            "bot_id": int(bot_id),
            "limit": int(limit),
            "offset": int(offset),
        }
        if task_type is not None:
            params["task_type"] = str(task_type)
        d = await self._get("/api/tasks/list", params=params, need_auth=True)
        return [TaskListItem(id=int(i.get("id", 0)), text=str(i.get("text", ""))) for i in d or []]

    async def tasks_info(self, user_id: int, bot_id: int, task_type: str, task_id: int) -> TaskInfoResult:
        params = {
            "user_id": int(user_id),
            "bot_id": int(bot_id),
            "task_type": str(task_type),
            "task_id": int(task_id),
        }
        d = await self._get("/api/tasks/info", params=params, need_auth=True)
        return TaskInfoResult(text=str(d.get("text", "")))

    async def tasks_log(
        self, user_id: int, task_type: str, task_id: int, bot_id: int
    ) -> Tuple[Optional[str], bytes]:
        """
        GET /api/tasks/log — скачивает лог и возвращает (filename, content_bytes).
        """
        params: Dict[str, Any] = {
            "user_id": int(user_id),
            "task_type": str(task_type),
            "task_id": int(task_id),
            "bot_id": int(bot_id),
        }
        content, headers = await self._get_file("/api/tasks/log", params=params, need_auth=True)
        fname = parse_content_disposition(headers.get("content-disposition"))
        return fname, content

