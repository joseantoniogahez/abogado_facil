import logging
from typing import Any

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


def _is_sensitive_field(field_name: str) -> bool:
    normalized = field_name.lower().replace("-", "_")
    return any(marker in normalized for marker in _SENSITIVE_FIELD_MARKERS)


def _safe_fields(fields: dict[str, Any]) -> dict[str, Any]:
    return {key: "[REDACTED]" if _is_sensitive_field(key) else value for key, value in fields.items()}


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
        extra = " ".join(f"{key}={fields[key]}" for key in sorted(fields))
        logger.log(level, "event=%s layer=%s %s", event, layer, extra)
        return

    logger.log(level, "event=%s layer=%s", event, layer)
