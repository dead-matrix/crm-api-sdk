"""
Тестовый скрипт для проверки новых API методов:
1. GET /api/tasks/active - активные задачи пользователя
2. POST /api/users/{user_id}/access/extend - продление доступа
3. GET /api/dialogs/{department}/search - поиск диалогов
"""

from __future__ import annotations

import asyncio
import os
import logging

from dotenv import load_dotenv

from crm_api import CRMApiClient

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Тестовые параметры
TEST_USER_ID = 6810549591
TEST_SEARCH_QUERY = "68"
TEST_DEPARTMENT = "sales"


async def test_get_active_tasks(client: CRMApiClient) -> None:
    """Тест GET /api/tasks/active"""
    print("\n" + "=" * 60)
    print("Тест 1: GET /api/tasks/active")
    print("=" * 60)
    
    try:
        result = await client.get_active_tasks(user_id=TEST_USER_ID)
        print(f"✅ Успешно!")
        print(f"Тип результата: {type(result).__name__}")
        print(f"Текст активных задач (HTML):")
        print("-" * 40)
        print(result.text)
        print("-" * 40)
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")


async def test_extend_user_access(client: CRMApiClient) -> None:
    """Тест POST /api/users/{user_id}/access/extend"""
    print("\n" + "=" * 60)
    print("Тест 2: POST /api/users/{user_id}/access/extend")
    print("=" * 60)
    
    try:
        # Добавляем 1 день доступа для MainBot (bot_id=1)
        result = await client.extend_user_access(
            user_id=TEST_USER_ID,
            bot_id=1,
            days=1
        )
        print(f"✅ Успешно!")
        print(f"Тип результата: {type(result).__name__}")
        print(f"User ID: {result.user_id}")
        print(f"Новая дата окончания доступа: {result.access_end}")
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")


async def test_search_dialogs(client: CRMApiClient) -> None:
    """Тест GET /api/dialogs/{department}/search"""
    print("\n" + "=" * 60)
    print("Тест 3: GET /api/dialogs/{department}/search")
    print("=" * 60)
    
    try:
        result = await client.search_dialogs(
            department=TEST_DEPARTMENT,
            q=TEST_SEARCH_QUERY,
            offset=0
        )
        print(f"✅ Успешно!")
        print(f"Тип результата: {type(result).__name__}")
        print(f"Лимит: {result.limit}")
        print(f"Смещение: {result.offset}")
        print(f"Найдено диалогов: {len(result.dialogs)}")
        print("-" * 40)
        for i, dialog in enumerate(result.dialogs[:5], 1):  # Показываем первые 5
            print(f"{i}. User ID: {dialog.user_id}")
            print(f"   Имя: {dialog.full_name}")
            print(f"   Активная подписка: {dialog.has_active_subscription}")
            print(f"   Статус: {dialog.status} ({dialog.status_color})")
        if len(result.dialogs) > 5:
            print(f"   ... и ещё {len(result.dialogs) - 5} диалогов")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")


async def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ НОВЫХ API МЕТОДОВ")
    print("#" * 60)

    client = CRMApiClient(
        base_url="http://127.0.0.1:8000",
        staff_id=int(os.getenv("CRM_STAFF_ID")),
        service_token=os.getenv("CRM_SERVICE_TOKEN"),
    )
    
    try:
        await test_get_active_tasks(client)
        await test_extend_user_access(client)
        await test_search_dialogs(client)
    finally:
        await client.aclose()
    
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

