from __future__ import annotations

from typing import Dict

from ..models import CategoryBucket, ProductEntry


class CatalogAPI:
    # --------------- Catalog (Products) ---------------

    async def products_active(self) -> Dict[str, CategoryBucket]:
        data = await self._get("/api/products/active", params=None, need_auth=True)
        out: Dict[str, CategoryBucket] = {}
        for cat_key, bucket in (data or {}).items():
            products_map: Dict[str, ProductEntry] = {}
            for pid, p in (bucket.get("products") or {}).items():
                products_map[str(pid)] = ProductEntry(
                    title=p.get("title"),
                    price_minor=int(p.get("price_minor", 0)),
                    price_usd=p.get("price_usd"),
                )
            out[str(cat_key)] = CategoryBucket(title=bucket.get("title"), products=products_map)
        return out

