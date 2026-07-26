import asyncio
import json
import logging
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from app.core.common.ai_metrics import AIMetricsRegistry
from app.core.errors.services import InvalidInputError
from app.integrations import ai_providers
from app.integrations.ai_context import build_minimized_ai_context
from app.integrations.ai_providers import (
    AiProviderError,
    AiProviderErrorCode,
    AiTextRequest,
    GeminiProvider,
    MockProvider,
    OpenAIProvider,
)

REQUEST = AiTextRequest(
    context=build_minimized_ai_context(
        instruction="Summarize this",
        source_context={"matter_summary": "Private matter"},
        authorized_fields={"matter_summary"},
        necessary_fields={"matter_summary"},
    ),
    function="matter_summary",
    model="test-model",
    request_id="request-1",
    execution_id="a" * 32,
)
PROVIDER_API_KEY = "provider-secret"  # pragma: allowlist secret


def run(coroutine):
    return asyncio.run(coroutine)


def test_mock_provider_returns_normalized_response() -> None:
    response = run(MockProvider(response="safe mock").generate(REQUEST))
    assert response.provider == "mock"
    assert response.text == "safe mock"


def test_provider_records_success_and_normalized_failure_metrics() -> None:
    metrics = AIMetricsRegistry()
    run(MockProvider(response="safe mock", metrics=metrics).generate(REQUEST))
    with pytest.raises(AiProviderError):
        run(
            MockProvider(
                failure_code=AiProviderErrorCode.TIMEOUT,
                metrics=metrics,
            ).generate(REQUEST)
        )

    failure, success = metrics.snapshot()
    assert failure.key.provider == "mock"
    assert failure.key.function == REQUEST.function
    assert failure.key.outcome == "failure"
    assert failure.key.error_code == "provider_timeout"
    assert success.key.outcome == "success"
    assert success.key.error_code is None
    assert failure.call_count == success.call_count == 1
    assert failure.total_duration_ms >= 0
    assert success.total_duration_ms >= 0


def test_provider_request_rejects_arbitrary_context() -> None:
    with pytest.raises(InvalidInputError, match="must be minimized"):
        AiTextRequest(
            context="private prompt",  # type: ignore[arg-type]
            function="matter_summary",
            model="test-model",
            request_id="request-1",
            execution_id="a" * 32,
        )


def test_provider_request_rejects_unsafe_metric_function() -> None:
    with pytest.raises(InvalidInputError, match="safe metric label"):
        AiTextRequest(
            context=REQUEST.context,
            function="Private matter text",
            model="test-model",
            request_id="request-1",
            execution_id="a" * 32,
        )


def test_provider_logs_correlated_lifecycle_without_request_or_response_content() -> None:
    logger = MagicMock(spec=logging.Logger)
    response = run(MockProvider(response="private response", logger=logger).generate(REQUEST))

    assert response.text == "private response"
    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert "ai_provider_started" in log_text
    assert "ai_provider_succeeded" in log_text
    assert REQUEST.request_id in log_text
    assert REQUEST.execution_id in log_text
    assert REQUEST.context.render_untrusted_data() not in log_text
    assert response.text not in log_text


def test_openai_provider_builds_provider_payload_without_leaking_key() -> None:
    calls = []

    async def transport(url, headers, body):
        calls.append((url, headers, body))
        return 200, {"choices": [{"message": {"content": "result"}}]}

    response = run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="fallback", transport=transport).generate(REQUEST))
    assert response.text == "result"
    assert calls[0][0].endswith("/chat/completions")
    payload = json.loads(calls[0][2])
    assert payload["messages"][0]["role"] == "system"
    assert "Summarize this" in payload["messages"][0]["content"]
    assert "Private matter" not in payload["messages"][0]["content"]
    assert payload["messages"][1] == {
        "role": "user",
        "content": REQUEST.context.render_untrusted_data(),
    }
    assert "tools" not in payload
    assert payload["tool_choice"] == "none"
    assert calls[0][1]["Authorization"] == f"Bearer {PROVIDER_API_KEY}"


def test_gemini_provider_normalizes_response() -> None:
    async def transport(url, headers, body):
        assert url.endswith(":generateContent")
        assert PROVIDER_API_KEY not in url
        assert headers["x-goog-api-key"] == PROVIDER_API_KEY
        payload = json.loads(body)
        system_text = payload["systemInstruction"]["parts"][0]["text"]
        assert "Summarize this" in system_text
        assert "Private matter" not in system_text
        assert payload["contents"] == [
            {
                "role": "user",
                "parts": [{"text": REQUEST.context.render_untrusted_data()}],
            }
        ]
        assert "tools" not in payload
        return 200, {"candidates": [{"content": {"parts": [{"text": "gemini result"}]}}]}

    response = run(GeminiProvider(api_key=PROVIDER_API_KEY, model="gemini-test", transport=transport).generate(REQUEST))
    assert response.provider == "gemini"
    assert response.text == "gemini result"


def test_provider_failures_are_safe_and_retryable() -> None:
    async def transport(url, headers, body):
        return 503, {"error": "contains provider details"}

    with pytest.raises(AiProviderError, match="no está disponible") as error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=transport).generate(REQUEST))
    assert error.value.code is AiProviderErrorCode.UNAVAILABLE
    assert error.value.retryable is True
    assert PROVIDER_API_KEY not in str(error.value)


def test_invalid_provider_response_is_rejected() -> None:
    async def transport(url, headers, body):
        return 200, {"choices": []}

    with pytest.raises(AiProviderError, match="respuesta inválida") as error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=transport).generate(REQUEST))
    assert error.value.error_code == "provider_invalid_response"
    assert error.value.retryable is False


def test_empty_provider_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        OpenAIProvider(api_key=" ", model="test")


def test_default_transport_parses_json_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        @staticmethod
        def read():
            return b'{"ok": true}'

    monkeypatch.setattr(ai_providers, "urlopen", lambda *args, **kwargs: Response())
    assert run(ai_providers._default_transport("https://provider.test", {}, b"{}")) == (200, {"ok": True})


@pytest.mark.parametrize(
    "url",
    [
        "http://provider.test",
        "file:///tmp/provider.json",
        "custom://provider.test",
        "https:///missing-host",
        "https://[",
    ],
)
def test_default_transport_rejects_invalid_urls(
    url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_request(*args, **kwargs):
        pytest.fail("urlopen must not be called for a non-HTTPS provider URL")

    monkeypatch.setattr(ai_providers, "urlopen", unexpected_request)

    with pytest.raises(AiProviderError, match="configuración") as error:
        run(ai_providers._default_transport(url, {}, b"{}"))

    assert error.value.code is AiProviderErrorCode.CONFIGURATION_ERROR
    assert error.value.retryable is False


def test_default_transport_maps_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    def raise_http_error(*args, **kwargs):
        raise HTTPError("https://provider.test", 429, "rate limited", {}, BytesIO())

    monkeypatch.setattr(ai_providers, "urlopen", raise_http_error)
    assert run(ai_providers._default_transport("https://provider.test", {}, b"{}")) == (429, None)


def test_default_transport_maps_network_and_json_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import URLError

    monkeypatch.setattr(ai_providers, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(URLError("offline")))
    with pytest.raises(AiProviderError) as error:
        run(ai_providers._default_transport("https://provider.test", {}, b"{}"))
    assert error.value.code is AiProviderErrorCode.UNAVAILABLE
    assert error.value.retryable is True

    monkeypatch.setattr(ai_providers, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad json")))
    with pytest.raises(AiProviderError) as error:
        run(ai_providers._default_transport("https://provider.test", {}, b"{}"))
    assert error.value.code is AiProviderErrorCode.INVALID_RESPONSE
    assert error.value.retryable is False


def test_default_transport_maps_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ai_providers,
        "urlopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError("external timeout detail")),
    )

    with pytest.raises(AiProviderError) as error:
        run(ai_providers._default_transport("https://provider.test", {}, b"{}"))

    assert error.value.code is AiProviderErrorCode.TIMEOUT
    assert "external timeout detail" not in str(error.value)


@pytest.mark.parametrize("provider_class", [OpenAIProvider, GeminiProvider])
@pytest.mark.parametrize(
    ("status", "expected_code", "retryable"),
    [
        (400, AiProviderErrorCode.REQUEST_REJECTED, False),
        (401, AiProviderErrorCode.AUTHENTICATION_FAILED, False),
        (403, AiProviderErrorCode.AUTHENTICATION_FAILED, False),
        (408, AiProviderErrorCode.TIMEOUT, True),
        (429, AiProviderErrorCode.RATE_LIMITED, True),
        (500, AiProviderErrorCode.UNAVAILABLE, True),
        (503, AiProviderErrorCode.UNAVAILABLE, True),
        (504, AiProviderErrorCode.TIMEOUT, True),
    ],
)
def test_http_providers_share_error_taxonomy(provider_class, status, expected_code, retryable) -> None:
    async def transport(url, headers, body):
        return status, {"error": f"external detail {PROVIDER_API_KEY}"}

    with pytest.raises(AiProviderError) as error:
        run(provider_class(api_key=PROVIDER_API_KEY, model="test", transport=transport).generate(REQUEST))

    assert error.value.code is expected_code
    assert error.value.error_code == expected_code.value
    assert error.value.retryable is retryable
    assert PROVIDER_API_KEY not in str(error.value)
    assert "external detail" not in str(error.value)


def test_provider_maps_transport_errors() -> None:
    async def unexpected_error(url, headers, body):
        raise RuntimeError("provider internals")

    with pytest.raises(AiProviderError) as transport_error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=unexpected_error).generate(REQUEST))
    assert transport_error.value.code is AiProviderErrorCode.UNAVAILABLE
    assert transport_error.value.retryable is True

    async def timeout(url, headers, body):
        raise TimeoutError("provider timeout detail")

    with pytest.raises(AiProviderError) as timeout_error:
        run(GeminiProvider(api_key=PROVIDER_API_KEY, model="test", transport=timeout).generate(REQUEST))
    assert timeout_error.value.code is AiProviderErrorCode.TIMEOUT


def test_provider_rethrows_safe_provider_error() -> None:
    async def provider_error(url, headers, body):
        raise AiProviderError(AiProviderErrorCode.REQUEST_REJECTED)

    with pytest.raises(AiProviderError) as error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=provider_error).generate(REQUEST))
    assert error.value.code is AiProviderErrorCode.REQUEST_REJECTED
    assert error.value.retryable is False


def test_provider_observer_logs_unexpected_error_type_without_message() -> None:
    logger = MagicMock(spec=logging.Logger)
    provider = MockProvider(logger=logger)

    async def unexpected() -> str:
        raise RuntimeError("private unexpected detail")

    with pytest.raises(RuntimeError, match="private unexpected detail"):
        run(provider._observe(REQUEST, model=REQUEST.model, operation=unexpected))

    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert "RuntimeError" in log_text
    assert "private unexpected detail" not in log_text


def test_response_text_parser_rejects_wrong_shape_and_blank_text() -> None:
    with pytest.raises(AiProviderError, match="respuesta inválida"):
        ai_providers._require_text("not-an-object", "value")
    with pytest.raises(AiProviderError, match="respuesta inválida"):
        ai_providers._require_text({"value": "  "}, "value")


@pytest.mark.parametrize("code", list(AiProviderErrorCode))
def test_mock_provider_uses_same_public_failure_contract(code: AiProviderErrorCode) -> None:
    logger = MagicMock(spec=logging.Logger)
    with pytest.raises(AiProviderError) as error:
        run(MockProvider(failure_code=code, logger=logger).generate(REQUEST))

    failure = error.value.to_public_failure()
    assert failure.code == code.value
    assert failure.message == str(error.value)
    assert failure.retryable is error.value.retryable
    assert PROVIDER_API_KEY not in repr(failure)
    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert code.value in log_text
    assert failure.message not in log_text
