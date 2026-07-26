import logging
from unittest.mock import MagicMock

import pytest

from app.core.common.observability import (
    AiCorrelationContext,
    is_safe_correlation_id,
    log_ai_event,
    log_layer_event,
    normalize_request_id,
)


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

    log_layer_event(logger, layer="ai_provider", event="heartbeat")
    assert logger.log.call_args.args == (logging.INFO, "event=%s layer=%s", "heartbeat", "ai_provider")

    log_layer_event(logger, layer="ai_provider", event="completed", model="safe\nforged=true")
    assert "\n" not in logger.log.call_args.args[-1]
    assert 'model="safe\\nforged=true"' in logger.log.call_args.args[-1]


def test_ai_correlation_context_rejects_log_injection_and_normalizes_request_ids() -> None:
    assert is_safe_correlation_id("request-1") is True
    assert normalize_request_id(" request-1 ") == "request-1"

    generated = normalize_request_id("request-1\nforged=true")
    assert len(generated) == 32
    assert generated != "request-1\nforged=true"

    with pytest.raises(ValueError, match="request_id"):
        AiCorrelationContext(request_id="unsafe value", execution_id="a" * 32)
    with pytest.raises(ValueError, match="execution_id"):
        AiCorrelationContext(request_id="request-1", execution_id="")


def test_log_ai_event_always_includes_correlation_and_redacts_fields() -> None:
    logger = MagicMock(spec=logging.Logger)
    log_ai_event(
        logger,
        layer="ai_provider",
        event="ai_provider_failed",
        correlation=AiCorrelationContext(request_id="request-1", execution_id="a" * 32),
        error_code="provider_timeout",
        prompt="private facts",
    )

    message = str(logger.log.call_args)
    assert "request-1" in message
    assert "a" * 32 in message
    assert "provider_timeout" in message
    assert "private facts" not in message
