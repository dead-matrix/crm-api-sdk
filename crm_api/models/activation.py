from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class ActivationRedeemInput:
    token: str
    recipient_user_id: int
    bot_id: int


@dataclass
class ActivationRedeemResult:
    """
    Результат redeem ACT_-токена (deep-link активации после оплаты).

    `success`=True - код активирован, доступ выдан.
    `success`=False - см. error_code:
      invalid_token | expired | already_used | not_found |
      wrong_bot | wrong_recipient.
    """
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    user_id: Optional[int] = None
    bot_id: Optional[int] = None
    action: Optional[str] = None  # "add" | "extend"
    access: Optional[Any] = None
    access_end: Optional[datetime] = None
    quantity: Optional[int] = None  # кол-во месяцев (срок = quantity*30 дней)
    activation_code_id: Optional[int] = None
    payment_id: Optional[int] = None
    # True — повтор уже использованного кода тем же получателем (ретрай SDK при
    # потерянном ответе / повторный клик): CRM вернул ранее выданный доступ
    # вместо 409 'already_used'. На свежем redeem отсутствует (None).
    idempotent_replay: Optional[bool] = None
