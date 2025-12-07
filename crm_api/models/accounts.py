from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class DayTotal:
    day: int
    total: int


@dataclass
class AccountItem:
    session_name: Optional[str]
    valid: bool
    spam_block: bool
    is_connected: bool
    location: Optional[str]
    full_name: Optional[str]
    username: Optional[str]
    phone: Optional[str]
    premium: bool
    commented: DayTotal
    invited: DayTotal
    stories: DayTotal
    tagged: DayTotal
    views: DayTotal
    reactions: DayTotal


# -------- Profile --------

@dataclass
class ProfileStatistics:
    subscriber: bool
    all_accounts_amount: int
    all_invited: int
    all_commented: int
    all_stories: int
    all_tagged: int
    all_views: int
    all_reactions: int
    tasks: int
    valid: int
    work: int
    invalid: int
    spam_block: int
    invited: int
    commented: int
    stories: int
    tagged: int
    views: int
    reactions: int
    quota: Optional[int]


@dataclass
class PosterAccount:
    telegram_id: Optional[int]
    valid: bool
    is_connected: bool
    last_connection: Optional[datetime]
    premium: bool
    full_name: Optional[str]
    username: Optional[str]
    location: Optional[str]


@dataclass
class PosterSubscription:
    active: bool
    access: Optional[Any]
    access_end: Optional[datetime]


@dataclass
class Bot3Summary:
    subscription: PosterSubscription
    account: Optional[PosterAccount]
    tasks: Dict[str, int]

