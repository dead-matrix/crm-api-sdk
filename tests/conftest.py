"""
Shared fixtures and utilities for CRM API SDK tests.
"""
from __future__ import annotations

import sys
import pathlib
from typing import Any, Callable, Dict

import httpx
import pytest

# Ensure repo root on path for imports
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from crm_api.client import CRMApiClient


def make_mock_transport(
    routes: Dict[str, Callable[[httpx.Request], httpx.Response]]
) -> httpx.MockTransport:
    """
    Create a MockTransport from a dict of route handlers.
    
    Routes dict keys are "METHOD /path" strings, e.g. "GET /api/users/1".
    Values are callables (request) -> Response.
    
    A default auth handler is always included.
    """
    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        method = req.method
        
        # Default auth handler
        if path.startswith("/api/staff/") and path.endswith("/auth") and method == "POST":
            data = {"token": "test-jwt-token", "expires_at": "2030-01-01T00:00:00+00:00"}
            return httpx.Response(200, json={"status": "success", "data": data})
        
        # Check custom routes
        key = f"{method} {path}"
        if key in routes:
            return routes[key](req)
        
        # Fallback: check path-only routes (for dynamic paths)
        for route_key, route_handler in routes.items():
            route_method, route_path = route_key.split(" ", 1)
            if route_method == method and _path_matches(route_path, path):
                return route_handler(req)
        
        return httpx.Response(404, json={"status": "error", "message": f"not found: {path}"})
    
    return httpx.MockTransport(handler)


def _path_matches(pattern: str, path: str) -> bool:
    """Simple path matching with {param} placeholders."""
    pattern_parts = pattern.split("/")
    path_parts = path.split("/")
    if len(pattern_parts) != len(path_parts):
        return False
    for pp, pathp in zip(pattern_parts, path_parts):
        if pp.startswith("{") and pp.endswith("}"):
            continue  # wildcard
        if pp != pathp:
            return False
    return True


def success_response(data: Any) -> httpx.Response:
    """Create a success envelope response."""
    return httpx.Response(200, json={"status": "success", "data": data})


def error_response(message: str, code: str = None, status: int = 400) -> httpx.Response:
    """Create an error envelope response."""
    payload = {"status": "error", "message": message}
    if code:
        payload["code"] = code
    return httpx.Response(status, json=payload)


@pytest.fixture
def client_factory():
    """Factory fixture to create CRMApiClient with custom mock transport."""
    def _create(routes: Dict[str, Callable[[httpx.Request], httpx.Response]]):
        transport = make_mock_transport(routes)
        return CRMApiClient(
            base_url="https://test-crm.example",
            staff_id=1,
            service_token="test-service-token",
            transport=transport,
        )
    return _create

