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
    transfer_link: str

