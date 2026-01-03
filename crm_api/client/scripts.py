from __future__ import annotations

from typing import List

from ..models import ScriptItem, ScriptFull, PriceMediaItem, ToolsMediaItem, ToolsMediaResult


class ScriptsAPI:
    """
    API для работы со скриптами быстрых ответов.
    
    Эндпоинты:
    - GET /api/scripts - список текстовых скриптов (отсортирован по частоте использования)
    - GET /api/scripts/{id} - полный текст скрипта (+ инкремент счётчика использования)
    - POST /api/scripts - создание нового текстового скрипта
    - POST /api/scripts/price - картинки с ценами для выбранных опций
    - POST /api/scripts/tools - видео с обзорами для выбранных опций
    
    Опции для price/tools:
    - 0: Масслукинг
    - 1: Отметки в истории
    - 2: Комментинг
    - 3: Инвайтинг
    - 4: Граббер
    """

    async def scripts_list(self) -> List[ScriptItem]:
        """
        Получить список всех текстовых скриптов.
        Скрипты отсортированы по частоте использования текущим сотрудником.
        """
        data = await self._get("/api/scripts", params=None, need_auth=True)
        return [ScriptItem(id=item["id"], title=item["title"], creator=item.get("creator")) for item in data]

    async def scripts_get(self, script_id: int) -> ScriptFull:
        """
        Получить полный текст скрипта по ID.
        При каждом вызове инкрементируется счётчик использования.
        """
        data = await self._get(f"/api/scripts/{script_id}", params=None, need_auth=True)
        return ScriptFull(id=data["id"], title=data["title"], text=data["text"])

    async def scripts_create(self, title: str, text: str) -> ScriptFull:
        """
        Создать новый текстовый скрипт.
        
        Args:
            title: Название скрипта (1-255 символов)
            text: Текст скрипта (1-4096 символов)
        
        Returns:
            Созданный скрипт с ID, названием и текстом.
        """
        data = await self._post("/api/scripts", {"title": title, "text": text}, need_auth=True)
        return ScriptFull(id=data["id"], title=data["title"], text=data["text"])

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
            содержащих video_url и file_id для отправки через Telegram.
        """
        data = await self._post("/api/scripts/tools", {"options": options, "bot_id": bot_id}, need_auth=True)
        media_items = [ToolsMediaItem(video_url=item["video_url"], file_id=item["file_id"]) for item in data["media"]]
        return ToolsMediaResult(text=data["text"], media=media_items)
