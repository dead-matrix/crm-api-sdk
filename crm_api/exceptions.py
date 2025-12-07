from __future__ import annotations


class SDKError(Exception):
    """Базовое исключение SDK."""


class ConfigError(SDKError):
    """Конфигурационная ошибка (например, отсутствует SERVICE_TOKEN)."""


class AuthError(SDKError):
    """Ошибки аутентификации/авторизации."""


class ApiError(SDKError):
    """Бизнес-ошибки API (status=error или наши проверки)."""

    def __init__(self, message: str, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.status = status


class HttpError(SDKError):
    """HTTP ошибки транспорта."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class ValidationError(SDKError):
    """Ошибки валидации входных данных SDK."""
