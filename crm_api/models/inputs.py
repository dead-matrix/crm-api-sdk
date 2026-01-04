from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Literal, List

from pydantic import BaseModel, Field, field_validator


class CreateUserInput(BaseModel):
    """Входная модель для POST /api/users."""
    user_id: int = Field(ge=1)
    full_name: str = Field(min_length=1, max_length=128)
    username: Optional[str] = Field(default=None, max_length=128)
    bot_id: int = Field(ge=1)
    refer: Optional[str] = Field(default=None, max_length=32)

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()


class UpdateUserInput(BaseModel):
    """Входная модель для PUT /api/users/{user_id}."""
    full_name: str = Field(min_length=1, max_length=128)
    username: Optional[str] = Field(default=None, max_length=128)

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()


ActionType = Literal["add", "extend", "revoke", "refund"]


class AddAccessInput(BaseModel):
    """Входная модель для POST /api/access/add."""
    user_id: int = Field(ge=1)
    bot_id: int = Field(ge=1)
    action: ActionType
    access: Optional[Any] = None
    action_date: Optional[datetime] = None
    access_end: Optional[datetime] = None
    payment_id: Optional[int] = Field(default=None, ge=1)
    ref: Optional[str] = Field(default=None, max_length=2048)

    @field_validator("action", mode="before")
    @classmethod
    def _normalize_action(cls, v: str) -> str:
        # Нормализуем и валидируем значения (разрешены add|extend|revoke|refund)
        if v is None:
            return v
        val = str(v).strip().lower()
        allowed = {"add", "extend", "revoke", "refund"}
        if val not in allowed:
            raise ValueError("action must be one of: add, extend, revoke, refund")
        return val


# -------- Payments inputs --------

class PaymentsCalculateInput(BaseModel):
    product_ids: List[int] = Field(min_length=1)
    discount_percent: int = Field(ge=0, le=90)
    months: int = Field(ge=1)


class InvoiceDraftInput(BaseModel):
    client_id: int = Field(ge=1)
    product_ids: List[int] = Field(min_length=1)
    discount_percent: int = Field(ge=0, le=90)
    months: int = Field(ge=1)
    provider: Literal["yookassa", "cryptocloud", "heleket"]


class InvoiceIssueInput(BaseModel):
    uuid: str = Field(min_length=20, max_length=64)
    client_email: str = Field(min_length=3, max_length=128)


class RefundInput(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=512)
    amount_minor: Optional[int] = Field(default=None, ge=1)

