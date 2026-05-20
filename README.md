# CRM API SDK (Python)

Небольшой асинхронный SDK для работы с CRM API.

- Только библиотека для импортирования (CLI нет)
- Python >= 3.10
- Типы доступны (PEP 561)
- SDK не читает .env и переменные окружения — передавайте параметры явно

## Установка

```bash
pip install .            # локальная установка из корня репозитория
# либо
pip install -e .         # установка для разработки (editable)
```

## Быстрый старт

```python
from crm_api import CRMApiClient

async with CRMApiClient(
    base_url="https://your-crm.example",
    staff_id=123,
    service_token="YOUR_SERVICE_TOKEN",
) as client:
    user = await client.get_user(7014133383)
    print(user)
```

Больше примеров см. в папке `examples/`.

## Платёжные провайдеры

SDK поддерживает те же провайдеры, что и CRM API — они указываются через
типизированный `Literal` (pydantic провалидирует значение ещё до HTTP-запроса):

```python
from crm_api import InvoiceDraftInput, PaymentProvider

inp = InvoiceDraftInput(
    client_id=123,
    product_ids=[1, 2],
    discount_percent=10,
    months=1,
    provider="platega",   # yookassa | cryptocloud | heleket | platega
)
```

`PaymentProvider` — публичный тип, можно импортировать напрямую:

```python
from typing import get_args
from crm_api import PaymentProvider
print(get_args(PaymentProvider))
# ('yookassa', 'cryptocloud', 'heleket', 'platega')
```

## Changelog

- **Unreleased** (`docs/SDK_PARITY.md` — детали и migration notes)
  - **BREAKING:** ряд полей в моделях ответа стал nullable, чтобы сервер
    `null` не превращался в строку `"None"` и сохранялся паритет с Go SDK:
    `CreateUserResult.full_name: str → Optional[str]`,
    `ListUserItem.full_name: str → Optional[str]`,
    `DialogSearchItem.status` / `status_color: str → Optional[str]`.
  - **BREAKING (минорно):** `AuthError` и `ValidationError` теперь
    несут атрибуты `code` и `status` (расширение сигнатуры конструктора
    с keyword-аргументами, обратно-совместимо для существующих
    вызывающих). Методы `activation_redeem`,
    `subscriptions_transfer_link`, `subscriptions_transfer_redeem`
    теперь корректно возвращают `Result(success=False, error_code=...)`
    для бизнес-ошибок HTTP 400/403/422, а не пробрасывают исключение.
  - Retry policy переписана без `tenacity`: идемпотентные методы
    (`GET`/`PUT`/`DELETE`) ретраятся на `{429, 502, 503, 504}`,
    транспортные ошибки — для любых методов. Паритет с Go SDK.
  - `clear_dialog_status` теперь шлёт явный `status_id: null` в body
    (сервер принимает оба варианта; единая форма упрощает диагностику).
  - `add_access` опускает опциональные `None`-поля вместо отправки
    `null` (`exclude_none=True`).
  - Удалена недостижимая backward-compat ветка в `get_payments`.

- **0.4.0**
  - **BREAKING:** `client.get_payments(...)` теперь возвращает
    `PaymentsListResult` (`limit`, `offset`, `count`, `items`) вместо
    плоского списка. Добавлены параметры `limit` (default 100_000) и
    `offset` (default 0).
- **0.3.0**
  - **BREAKING:** `CreateUserResult` расширен полями `user_id`, `full_name`,
    `username`, `bot_id`, `refer`, `date_reg`. `POST /api/users` теперь
    идемпотентен — при повторе на (user_id, bot_id) возвращает `created=False`
    и существующие данные без побочных эффектов.
  - Новый метод `client.list_users(bot_id, limit=100_000, offset=0)` →
    `ListUsersResult`. Каждый `ListUserItem` содержит флаг `restricted` —
    заблокированные юзеры (мессенджер не должен обрабатывать их сообщения).
  - Новый метод `client.get_monthly_sales()` → `MonthlySalesResult` —
    оплаченные платежи за текущий календарный месяц с `category`
    (`main`/`extra`/`other`) и `repeat_purchase` per-category. Атрибуцию
    к продавцу делает потребитель SDK на основании своих диалогов.
- **0.2.0** — добавлен `platega` в `InvoiceDraftInput.provider`; экспортирован тип
  `PaymentProvider`.
- **0.1.0** — первоначальный релиз.

## Примечания

- SDK не загружает `.env`. Если вам удобно хранить настройки в `.env`, загружайте их в своём скрипте и передавайте в конструктор клиента.
- Автор: Matrix
- Лицензия: Proprietary (закрытая)

