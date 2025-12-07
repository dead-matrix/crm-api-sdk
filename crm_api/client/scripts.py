from __future__ import annotations

from typing import List

from ..models import ScriptItem, ScriptFull, PriceMediaItem, ToolsMediaResult


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

    async def scripts_tools(self, options: List[int]) -> ToolsMediaResult:
        """
        Получить видео с обзорами для выбранных опций.
        
        Args:
            options: Список ID опций (от 1 до 5 штук).
                     0=Масслукинг, 1=Отметки в истории, 2=Комментинг, 
                     3=Инвайтинг, 4=Граббер
        
        Returns:
            Объект с текстом (базовый + ссылки на обзоры) и массивом ссылок на видео.
        """
        data = await self._post("/api/scripts/tools", {"options": options}, need_auth=True)
        return ToolsMediaResult(text=data["text"], media=data["media"])
