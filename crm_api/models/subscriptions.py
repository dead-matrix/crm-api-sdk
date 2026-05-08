from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AccessPaymentRef:
    id: Optional[int]
    amount_minor: Optional[int]
    currency: Optional[str]
    status: Optional[str]
    date_paid: Optional[datetime]


@dataclass
class AccessStaffRef:
    id: Optional[int]
    name: Optional[str]


@dataclass
class AccessHistoryItem:
    action: str
    bot_id: int
    access: Optional[Any]
    action_date: Optional[datetime]
    access_end: Optional[datetime]
    payment: Optional[AccessPaymentRef]
    staff: Optional[AccessStaffRef]
    ref: Optional[str]


@dataclass
class SubscriptionsHistoryResult:
    user_id: int
    history: List[AccessHistoryItem]


@dataclass
class AccessDefinitionsResult:
    main: Dict[str, str]
    poster: Dict[str, str]


@dataclass
class TransferLinkResult:
    """
    Результат запроса transfer-link.

    Старое поле `transfer_link` сохранено для бек-совместимости.
    Новые поля nullable — заполняются при успешном ответе CRM нового формата:
      - token: чистый TR_<base32> для боевого парсинга в боте
      - bot_id, expires_at, ttl_hours: метаданные

    Если CRM ответил ошибкой (например `not_supported` для bot_id=3
    или `no_subscription`), клиент получает `error_code` + `error_message`
    и transfer_link/token будут None.
    """
    transfer_link: Optional[str] = None
    token: Optional[str] = None
    bot_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    ttl_hours: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class TransferRedeemInput:
    token: str
    recipient_user_id: int
    bot_id: int


@dataclass
class TransferRedeemResult:
    """
    Результат redeem transfer-ссылки.

    `success`=True - доступ перенесён, в access/access_end заполнены данные.
    `success`=False - см. error_code:
      no_subscription | recipient_has_access | invalid_token | expired |
      wrong_bot | same_user | configuration_error.
    """
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    source_user_id: Optional[int] = None
    recipient_user_id: Optional[int] = None
    bot_id: Optional[int] = None
    access: Optional[Any] = None
    access_end: Optional[datetime] = None

