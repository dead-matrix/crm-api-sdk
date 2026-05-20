from __future__ import annotations


class SDKError(Exception):
    """Базовое исключение SDK."""


class ConfigError(SDKError):
    """Конфигурационная ошибка (например, отсутствует SERVICE_TOKEN)."""


class AuthError(SDKError):
    """Ошибки аутентификации/авторизации (HTTP 401/403)."""

    def __init__(self, message: str, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.status = status


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
    """
    Ошибки валидации входных данных (HTTP 400/422 или code=VALIDATION_ERROR).

    Поля `code`/`status` пробрасываются от сервера и могут быть None
    для исключений, поднятых локально на стороне SDK.
    """

    def __init__(self, message: str, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.status = status
