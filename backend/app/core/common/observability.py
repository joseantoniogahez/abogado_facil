import json
import logging
import re
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

_SENSITIVE_FIELD_MARKERS = (
    "api_key",
    "authorization",
    "credential",
    "document",
    "exception",
    "prompt",
    "secret",
    "stack",
    "text",
    "token",
)
_CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")


def is_safe_correlation_id(value: str) -> bool:
    """Return whether a value is bounded and safe for structured logs."""

    return _CORRELATION_ID_PATTERN.fullmatch(value) is not None


def normalize_request_id(value: str | None) -> str:
    """Reuse a safe caller ID or replace it with an opaque server-generated ID."""

    candidate = (value or "").strip()
    return candidate if is_safe_correlation_id(candidate) else uuid4().hex


@dataclass(frozen=True)
class AiCorrelationContext:
    """Identifiers shared by API, persistence, queue, worker, and provider logs."""

    request_id: str
    execution_id: str

    def __post_init__(self) -> None:
        if not is_safe_correlation_id(self.request_id):
            raise ValueError("request_id is not a safe correlation identifier")
        if not is_safe_correlation_id(self.execution_id):
            raise ValueError("execution_id is not a safe correlation identifier")


def _is_sensitive_field(field_name: str) -> bool:
    normalized = field_name.lower().replace("-", "_")
    return any(marker in normalized for marker in _SENSITIVE_FIELD_MARKERS)


def _safe_fields(fields: dict[str, Any]) -> dict[str, Any]:
    return {key: "[REDACTED]" if _is_sensitive_field(key) else value for key, value in fields.items()}


def _format_field_value(value: Any) -> Any:
    return json.dumps(value, ensure_ascii=False) if isinstance(value, str) else value


def log_layer_event(
    logger: logging.Logger,
    *,
    layer: str,
    event: str,
    level: int = logging.INFO,
    **fields: Any,
) -> None:
    fields = _safe_fields(fields)
    if fields:
        extra = " ".join(f"{key}={_format_field_value(fields[key])}" for key in sorted(fields))
        logger.log(level, "event=%s layer=%s %s", event, layer, extra)
        return

    logger.log(level, "event=%s layer=%s", event, layer)


def log_ai_event(
    logger: logging.Logger,
    *,
    layer: str,
    event: str,
    correlation: AiCorrelationContext,
    level: int = logging.INFO,
    **fields: Any,
) -> None:
    """Log an AI event with the mandatory correlation pair and redaction."""

    log_layer_event(
        logger,
        layer=layer,
        event=event,
        level=level,
        request_id=correlation.request_id,
        execution_id=correlation.execution_id,
        **fields,
    )
