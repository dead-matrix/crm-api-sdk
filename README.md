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

## Примечания

- SDK не загружает `.env`. Если вам удобно хранить настройки в `.env`, загружайте их в своём скрипте и передавайте в конструктор клиента.
- Автор: Matrix
- Лицензия: Proprietary (закрытая)

