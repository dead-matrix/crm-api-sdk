"""
Тестовый скрипт для проверки обновлённого метода scripts_tools:
POST /api/scripts/tools - видео с обзорами для выбранных опций

Изменения в API:
- Добавлен обязательный параметр bot_id
- media теперь возвращает объекты с video_url и file_id
"""

from __future__ import annotations

import asyncio
import os
import logging

from dotenv import load_dotenv

from crm_api import CRMApiClient, ToolsMediaItem, ToolsMediaResult

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Тестовые параметры
TEST_OPTIONS = [0, 1]  # Масслукинг, Отметки в истории
TEST_BOT_ID = 7662403109  # Поддерживаемый bot_id


async def test_scripts_tools(client: CRMApiClient) -> None:
    """Тест POST /api/scripts/tools с новым форматом ответа"""
    print("\n" + "=" * 60)
    print("Тест: POST /api/scripts/tools")
    print("=" * 60)
    print(f"Параметры: options={TEST_OPTIONS}, bot_id={TEST_BOT_ID}")
    print("-" * 40)
    
    try:
        result = await client.scripts_tools(options=TEST_OPTIONS, bot_id=TEST_BOT_ID)
        
        print(f"✅ Успешно!")
        print(f"Тип результата: {type(result).__name__}")
        assert isinstance(result, ToolsMediaResult), f"Ожидался ToolsMediaResult, получен {type(result)}"
        
        print(f"\nТекст:")
        print("-" * 40)
        print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
        print("-" * 40)
        
        print(f"\nМедиа ({len(result.media)} элементов):")
        print("-" * 40)
        for i, media_item in enumerate(result.media, 1):
            assert isinstance(media_item, ToolsMediaItem), f"Ожидался ToolsMediaItem, получен {type(media_item)}"
            print(f"{i}. video_url: {media_item.video_url}")
            print(f"   file_id: {media_item.file_id[:50]}..." if len(media_item.file_id) > 50 else f"   file_id: {media_item.file_id}")
        print("-" * 40)
        
        print("\n✅ Все проверки пройдены!")
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def test_scripts_tools_all_options(client: CRMApiClient) -> None:
    """Тест POST /api/scripts/tools со всеми опциями"""
    print("\n" + "=" * 60)
    print("Тест: POST /api/scripts/tools (все опции)")
    print("=" * 60)
    
    all_options = [0, 1, 2, 3, 4]  # Все доступные опции
    print(f"Параметры: options={all_options}, bot_id={TEST_BOT_ID}")
    print("-" * 40)
    
    try:
        result = await client.scripts_tools(options=all_options, bot_id=TEST_BOT_ID)
        
        print(f"✅ Успешно!")
        print(f"Количество видео: {len(result.media)}")
        
        for i, media_item in enumerate(result.media, 1):
            print(f"{i}. {media_item.video_url.split('/')[-1]}")
        
        print("\n✅ Все проверки пройдены!")
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ scripts_tools (ОБНОВЛЁННЫЙ API)")
    print("#" * 60)

    client = CRMApiClient(
        base_url="http://127.0.0.1:8000",
        staff_id=int(os.getenv("CRM_STAFF_ID")),
        service_token=os.getenv("CRM_SERVICE_TOKEN"),
    )
    
    try:
        await test_scripts_tools(client)
        await test_scripts_tools_all_options(client)
    finally:
        await client.aclose()
    
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

