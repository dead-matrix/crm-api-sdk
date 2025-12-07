from __future__ import annotations

from typing import Optional

from ..models import PromptUpdateResult


class PromptsAPI:
    # --------------- Prompts ---------------

    async def prompt_get(self, user_id: int) -> Optional[str]:
        d = await self._get("/api/prompt", params={"user_id": int(user_id)}, need_auth=True)
        return d

    async def prompt_update(self, user_id: int, prompt: str) -> PromptUpdateResult:
        d = await self._post(
            "/api/prompt/update",
            {"prompt": prompt},
            need_auth=True,
            params={"user_id": int(user_id)},
        )
        return PromptUpdateResult(
            reset=d.get("reset"),
            message=d.get("message"),
            updated=d.get("updated"),
            created=d.get("created"),
        )

