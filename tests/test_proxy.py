"""Tests for ProxyAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response


class TestProxyAPI:
    @pytest.mark.asyncio
    async def test_proxy_check_success(self, client_factory):
        """Test proxy_check returns ProxyCheckResult."""
        mock_data = {
            "checked": 3,
            "valid": 2,
            "invalid": 1,
            "results": [
                {"proxy": "1.2.3.4:8080", "valid": True, "ru_error": None, "location": "RU"},
                {"proxy": "5.6.7.8:3128", "valid": True, "ru_error": None, "location": "DE"},
                {"proxy": "9.10.11.12:1080", "valid": False, "ru_error": "Connection timeout", "location": None},
            ]
        }
        routes = {
            "POST /api/proxy/check": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.proxy_check(user_id=123)
            
            assert result.checked == 3
            assert result.valid == 2
            assert result.invalid == 1
            assert len(result.results) == 3
            
            r1 = result.results[0]
            assert r1.proxy == "1.2.3.4:8080"
            assert r1.valid is True
            assert r1.ru_error is None
            assert r1.location == "RU"
            
            r3 = result.results[2]
            assert r3.valid is False
            assert r3.ru_error == "Connection timeout"

    @pytest.mark.asyncio
    async def test_proxy_check_empty(self, client_factory):
        """Test proxy_check with no proxies."""
        mock_data = {
            "checked": 0,
            "valid": 0,
            "invalid": 0,
            "results": []
        }
        routes = {
            "POST /api/proxy/check": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.proxy_check(user_id=123)
            
            assert result.checked == 0
            assert result.results == []

    @pytest.mark.asyncio
    async def test_proxy_list_success(self, client_factory):
        """Test proxy_list returns list of ProxyItem."""
        mock_data = [
            {
                "type": "socks5",
                "ip": "1.2.3.4",
                "port": 1080,
                "login": "user1",
                "password": "pass1",
                "valid": True,
                "location": "RU",
            },
            {
                "type": "http",
                "ip": "5.6.7.8",
                "port": 8080,
                "login": None,
                "password": None,
                "valid": True,
                "location": "US",
            },
        ]
        routes = {
            "GET /api/proxy/list": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.proxy_list(user_id=123)
            
            assert len(result) == 2
            
            p1 = result[0]
            assert p1.type == "socks5"
            assert p1.ip == "1.2.3.4"
            assert p1.port == 1080
            assert p1.login == "user1"
            assert p1.password == "pass1"
            assert p1.valid is True
            assert p1.location == "RU"
            
            p2 = result[1]
            assert p2.type == "http"
            assert p2.login is None
            assert p2.password is None

    @pytest.mark.asyncio
    async def test_proxy_list_empty(self, client_factory):
        """Test proxy_list with no proxies."""
        routes = {
            "GET /api/proxy/list": lambda req: success_response([]),
        }
        async with client_factory(routes) as client:
            result = await client.proxy_list(user_id=123)
            assert result == []

