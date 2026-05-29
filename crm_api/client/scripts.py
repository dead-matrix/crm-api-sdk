from __future__ import annotations

from typing import List

from ..models import PriceMediaItem, ToolsMediaItem, ToolsMediaResult


class ScriptsAPI:
    """
    API для sales-decks (картинки с ценами и видео-обзоры).

    Эндпоинты:
    - POST /api/scripts/price - картинки с ценами для выбранных опций
    - POST /api/scripts/tools - видео с обзорами для выбранных опций

    Опции (общие для price и tools):
    - 0: Масслукинг
    - 1: Отметки в истории
    - 2: Комментинг
    - 3: Инвайтинг
    - 4: Граббер

    История: до Phase 5 этот класс также экспортировал
    ``scripts_list`` / ``scripts_get`` / ``scripts_create`` для legacy
    текстовых быстрых ответов под /api/scripts. Эти три метода удалены
    после миграции на reply templates (см. ``ReplyTemplatesAPI``);
    оставшиеся два метода — это sales decks (источник данных —
    ``app/data/scripts_data.json`` на стороне CRM-API), к быстрым
    ответам они отношения не имеют.
    """

    async def scripts_price(self, options: List[int]) -> List[PriceMediaItem]:
        """
        Получить картинки с ценами для выбранных опций.

        Args:
            options: Список ID опций (от 1 до 5 штук).
                     0=Масслукинг, 1=Отметки в истории, 2=Комментинг,
                     3=Инвайтинг, 4=Граббер

        Returns:
            Список элементов с текстом и массивом ссылок на картинки.
            Если выбраны опции 0-3 и 4 одновременно, вернётся 2 элемента.
        """
        data = await self._post("/api/scripts/price", {"options": options}, need_auth=True)
        return [PriceMediaItem(text=item["text"], media=item["media"]) for item in data]

    async def scripts_tools(self, options: List[int], bot_id: int) -> ToolsMediaResult:
        """
        Получить видео с обзорами для выбранных опций.

        Args:
            options: Список ID опций (от 1 до 5 штук).
                     0=Масслукинг, 1=Отметки в истории, 2=Комментинг,
                     3=Инвайтинг, 4=Граббер
            bot_id: ID Telegram бота для получения file_id видео.
                    Поддерживаемые значения: 7662403109, 8002165573

        Returns:
            Объект с текстом (базовый + ссылки на обзоры) и массивом объектов медиа,
            содержащих video_url, thumb (превью видео) и file_id для отправки через Telegram.
        """
        data = await self._post("/api/scripts/tools", {"options": options, "bot_id": bot_id}, need_auth=True)
        media_items = [
            ToolsMediaItem(video_url=item["video_url"], thumb=item["thumb"], file_id=item["file_id"])
            for item in data["media"]
        ]
        return ToolsMediaResult(text=data["text"], media=media_items)
