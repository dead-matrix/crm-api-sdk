from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ProductEntry:
    title: str
    price_minor: int
    price_usd: Optional[int]


@dataclass
class CategoryBucket:
    title: str
    products: Dict[str, ProductEntry]

