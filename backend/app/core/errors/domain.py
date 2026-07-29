from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from app.core.errors.base import AppError


class ErrorLayer(StrEnum):
    DOMAIN = "domain"
    ROUTER = "router"
    SERVICE = "service"
    REPOSITORY = "repository"


class DomainErrorType(StrEnum):
    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INTERNAL_ERROR = "internal_error"
    RATE_LIMITED = "rate_limited"
    PROVIDER_AUTHENTICATION_FAILED = "provider_authentication_failed"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_REQUEST_REJECTED = "provider_request_rejected"
    PROVIDER_INVALID_RESPONSE = "provider_invalid_response"
    PROVIDER_CONFIGURATION_ERROR = "provider_configuration_error"


class DomainError(AppError):
    def __init__(
        self,
        error_type: DomainErrorType,
        message: str,
        *,
        details: Any | None = None,
        headers: Mapping[str, str] | None = None,
        layer: ErrorLayer = ErrorLayer.DOMAIN,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.detail = message
        self.details = details
        self.meta = details
        self.code = error_type.value
        self.layer = layer
        self.headers = dict(headers) if headers is not None else None
