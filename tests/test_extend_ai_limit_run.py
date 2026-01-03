"""
Тестовый скрипт для проверки нового метода extend_ai_limit:
POST /api/users/{user_id}/ai-limit/extend - расширение AI квоты пользователя

Эндпоинт добавляет указанное количество миллионов символов к текущему лимиту ai_limit.
"""

from __future__ import annotations

import asyncio
import os
import logging

from dotenv import load_dotenv

from crm_api import CRMApiClient, ExtendAiLimitResult

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Тестовые параметры
TEST_USER_ID = 6810549591
TEST_MILLIONS = 1  # Добавляем 1 миллион символов


async def test_extend_ai_limit(client: CRMApiClient) -> None:
    """Тест POST /api/users/{user_id}/ai-limit/extend"""
    print("\n" + "=" * 60)
    print("Тест: POST /api/users/{user_id}/ai-limit/extend")
    print("=" * 60)
    print(f"Параметры: user_id={TEST_USER_ID}, millions={TEST_MILLIONS}")
    print("-" * 40)
    
    try:
        result = await client.extend_ai_limit(
            user_id=TEST_USER_ID,
            millions=TEST_MILLIONS
        )
        
        print(f"✅ Успешно!")
        print(f"Тип результата: {type(result).__name__}")
        assert isinstance(result, ExtendAiLimitResult), f"Ожидался ExtendAiLimitResult, получен {type(result)}"
        
        print(f"\nРезультат:")
        print("-" * 40)
        print(f"Предыдущий ai_limit: {result.previous_ai_limit} млн символов")
        print(f"Новый ai_limit: {result.ai_limit} млн символов")
        print(f"Добавлено: {result.ai_limit - result.previous_ai_limit} млн символов")
        print("-" * 40)
        
        # Проверяем, что лимит увеличился
        assert result.ai_limit >= result.previous_ai_limit, "ai_limit должен увеличиться"
        assert result.ai_limit == result.previous_ai_limit + TEST_MILLIONS, \
            f"ai_limit должен увеличиться на {TEST_MILLIONS}"
        
        print("\n✅ Все проверки пройдены!")
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def test_extend_ai_limit_multiple(client: CRMApiClient) -> None:
    """Тест POST /api/users/{user_id}/ai-limit/extend с разными значениями"""
    print("\n" + "=" * 60)
    print("Тест: POST /api/users/{user_id}/ai-limit/extend (5 млн)")
    print("=" * 60)
    
    millions = 5
    print(f"Параметры: user_id={TEST_USER_ID}, millions={millions}")
    print("-" * 40)
    
    try:
        result = await client.extend_ai_limit(
            user_id=TEST_USER_ID,
            millions=millions
        )
        
        print(f"✅ Успешно!")
        print(f"Предыдущий ai_limit: {result.previous_ai_limit}")
        print(f"Новый ai_limit: {result.ai_limit}")
        print(f"Добавлено: {result.ai_limit - result.previous_ai_limit} млн символов")
        
        print("\n✅ Все проверки пройдены!")
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ extend_ai_limit (НОВЫЙ ЭНДПОИНТ)")
    print("#" * 60)

    client = CRMApiClient(
        base_url="http://127.0.0.1:8000",
        staff_id=int(os.getenv("CRM_STAFF_ID")),
        service_token=os.getenv("CRM_SERVICE_TOKEN"),
    )
    
    try:
        await test_extend_ai_limit(client)
        await test_extend_ai_limit_multiple(client)
    finally:
        await client.aclose()
    
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

