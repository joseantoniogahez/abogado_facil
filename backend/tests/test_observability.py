import logging
from unittest.mock import MagicMock

from app.core.common.observability import log_layer_event


def test_log_layer_event_redacts_ai_sensitive_fields() -> None:
    logger = MagicMock(spec=logging.Logger)
    log_layer_event(
        logger,
        layer="ai_provider",
        event="request_failed",
        request_id="request-1",
        provider="openai",
        prompt="private legal facts",
        document_text="confidential document",
        api_key="provider-secret",  # pragma: allowlist secret
        exception="provider response body",
    )
    message = str(logger.log.call_args)
    assert "request-1" in message and "openai" in message
    for sensitive_value in (
        "private legal facts",
        "confidential document",
        "provider-secret",
        "provider response body",
    ):
        assert sensitive_value not in message
    assert message.count("[REDACTED]") == 4


def test_log_layer_event_preserves_non_sensitive_operational_fields() -> None:
    logger = MagicMock(spec=logging.Logger)
    log_layer_event(logger, layer="ai_provider", event="completed", status_code=200, duration_ms=12.5)
    message = str(logger.log.call_args)
    assert "status_code=200" in message and "duration_ms=12.5" in message
