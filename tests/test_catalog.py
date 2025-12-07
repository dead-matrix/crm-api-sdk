"""Tests for CatalogAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestCatalogAPI:
    @pytest.mark.asyncio
    async def test_products_active_success(self, client_factory):
        """Test products_active returns properly mapped CategoryBucket dict."""
        mock_data = {
            "main": {
                "title": "Основные продукты",
                "products": {
                    "1": {"title": "Масслукинг", "price_minor": 99000, "price_usd": 10.0},
                    "2": {"title": "Инвайтинг", "price_minor": 149000, "price_usd": 15.0},
                }
            },
            "poster": {
                "title": "Постер",
                "products": {
                    "10": {"title": "Постер базовый", "price_minor": 49000, "price_usd": 5.0},
                }
            }
        }
        routes = {
            "GET /api/products/active": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.products_active()
            
            assert "main" in result
            assert "poster" in result
            
            main = result["main"]
            assert main.title == "Основные продукты"
            assert "1" in main.products
            assert "2" in main.products
            
            p1 = main.products["1"]
            assert p1.title == "Масслукинг"
            assert p1.price_minor == 99000
            assert p1.price_usd == 10.0
            
            p2 = main.products["2"]
            assert p2.title == "Инвайтинг"
            assert p2.price_minor == 149000
            assert p2.price_usd == 15.0
            
            poster = result["poster"]
            assert poster.title == "Постер"
            assert "10" in poster.products
            assert poster.products["10"].title == "Постер базовый"

    @pytest.mark.asyncio
    async def test_products_active_empty(self, client_factory):
        """Test products_active with empty response."""
        routes = {
            "GET /api/products/active": lambda req: success_response({}),
        }
        async with client_factory(routes) as client:
            result = await client.products_active()
            assert result == {}

    @pytest.mark.asyncio
    async def test_products_active_missing_products(self, client_factory):
        """Test products_active handles category without products."""
        mock_data = {
            "empty_cat": {
                "title": "Empty Category",
                # No products key
            }
        }
        routes = {
            "GET /api/products/active": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.products_active()
            
            assert "empty_cat" in result
            assert result["empty_cat"].title == "Empty Category"
            assert result["empty_cat"].products == {}

    @pytest.mark.asyncio
    async def test_products_active_missing_price_fields(self, client_factory):
        """Test products_active handles missing price fields."""
        mock_data = {
            "cat": {
                "title": "Test",
                "products": {
                    "1": {"title": "Product"},  # Missing price_minor and price_usd
                }
            }
        }
        routes = {
            "GET /api/products/active": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.products_active()
            
            p = result["cat"].products["1"]
            assert p.title == "Product"
            assert p.price_minor == 0
            assert p.price_usd is None

