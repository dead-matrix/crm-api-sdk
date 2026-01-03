"""
Тестовый скрипт для проверки обновлённых методов API платежей:
- GET /api/payments/invoice/{uuid} - информация о платеже
- GET /api/payments - история платежей

Проверяем новые поля: client_email, referer_id, staff_id, fx_rate_rub_usd, 
status_ru, description, pay_link, date_invoiced, date_paid
"""

from __future__ import annotations

import asyncio
import os
import logging

from dotenv import load_dotenv

from crm_api import CRMApiClient, InvoiceInfoResult, PaymentHistoryItem

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Тестовые параметры
TEST_USER_ID = 6810549591


async def test_get_payments(client: CRMApiClient) -> str | None:
    """Тест GET /api/payments - история платежей"""
    print("\n" + "=" * 60)
    print("Тест: GET /api/payments")
    print("=" * 60)
    
    try:
        # Получаем все платежи
        payments = await client.get_payments()
        
        print(f"✅ Успешно!")
        print(f"Всего платежей: {len(payments)}")
        
        if payments:
            p = payments[0]
            assert isinstance(p, PaymentHistoryItem), f"Ожидался PaymentHistoryItem, получен {type(p)}"
            
            print(f"\nПервый платёж:")
            print("-" * 40)
            print(f"UUID: {p.uuid}")
            print(f"Статус: {p.status} ({p.status_ru})")
            print(f"Client ID: {p.client_id}")
            print(f"Client Email: {p.client_email}")
            print(f"Referer ID: {p.referer_id}")
            print(f"Staff ID: {p.staff_id}")
            print(f"Сумма: {p.amount_minor / 100:.2f} {p.currency}")
            print(f"FX Rate RUB/USD: {p.fx_rate_rub_usd}")
            print(f"Скидка: {p.discount_percent}%")
            print(f"Описание: {p.description[:50] if p.description else None}...")
            print(f"Провайдер: {p.provider}")
            print(f"Pay Link: {p.pay_link}")
            print(f"Дата создания: {p.date_create}")
            print(f"Дата выставления: {p.date_invoiced}")
            print(f"Дата оплаты: {p.date_paid}")
            print(f"Активации: {len(p.activation)} шт.")
            print("-" * 40)
            
            return p.uuid
        return None
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def test_get_payments_by_user(client: CRMApiClient) -> None:
    """Тест GET /api/payments?user_id=... - платежи пользователя"""
    print("\n" + "=" * 60)
    print(f"Тест: GET /api/payments?user_id={TEST_USER_ID}")
    print("=" * 60)
    
    try:
        payments = await client.get_payments(user_id=TEST_USER_ID)
        
        print(f"✅ Успешно!")
        print(f"Платежей пользователя {TEST_USER_ID}: {len(payments)}")
        
        for i, p in enumerate(payments[:3], 1):
            print(f"\n{i}. {p.uuid[:20]}... - {p.status_ru} - {p.amount_minor/100:.2f} RUB")
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def test_get_invoice_info(client: CRMApiClient, uuid: str) -> None:
    """Тест GET /api/payments/invoice/{uuid} - информация о платеже"""
    print("\n" + "=" * 60)
    print(f"Тест: GET /api/payments/invoice/{uuid[:20]}...")
    print("=" * 60)
    
    try:
        info = await client.get_invoice_info(uuid)
        
        print(f"✅ Успешно!")
        assert isinstance(info, InvoiceInfoResult), f"Ожидался InvoiceInfoResult, получен {type(info)}"
        
        print(f"\nИнформация о платеже:")
        print("-" * 40)
        print(f"UUID: {info.uuid}")
        print(f"Статус: {info.status} ({info.status_ru})")
        print(f"Client ID: {info.client_id}")
        print(f"Client Email: {info.client_email}")
        print(f"Referer ID: {info.referer_id}")
        print(f"Staff ID: {info.staff_id}")
        print(f"Сумма: {info.amount_minor / 100:.2f} {info.currency}")
        print(f"FX Rate RUB/USD: {info.fx_rate_rub_usd}")
        print(f"Скидка: {info.discount_percent}%")
        print(f"Описание: {info.description[:80] if info.description else None}...")
        print(f"Провайдер: {info.provider}")
        print(f"Pay Link: {info.pay_link}")
        print(f"Дата создания: {info.date_create}")
        print(f"Дата выставления: {info.date_invoiced}")
        print(f"Дата оплаты: {info.date_paid}")
        print(f"Позиций: {len(info.items)}")
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        raise


async def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ ОБНОВЛЁННОГО API ПЛАТЕЖЕЙ")
    print("#" * 60)

    client = CRMApiClient(
        base_url="http://127.0.0.1:8000",
        staff_id=int(os.getenv("CRM_STAFF_ID")),
        service_token=os.getenv("CRM_SERVICE_TOKEN"),
    )
    
    try:
        uuid = await test_get_payments(client)
        await test_get_payments_by_user(client)
        if uuid:
            await test_get_invoice_info(client, uuid)
    finally:
        await client.aclose()
    
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

