import asyncio
import logging
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import openai
import pytest
from google.genai import errors as genai_errors

from app.core.common.ai_metrics import AIMetricsRegistry
from app.core.errors.services import InvalidInputError
from app.integrations import ai_providers
from app.integrations.ai_context import MinimizedAIContext, build_minimized_ai_context
from app.integrations.ai_providers import (
    AiProviderError,
    AiProviderErrorCode,
    AiTextRequest,
    GeminiProvider,
    MockProvider,
    OpenAIProvider,
    list_gemini_models,
    list_openai_models,
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


def openai_client(*, response=None, error: Exception | None = None):
    create = AsyncMock(return_value=response)
    create.side_effect = error
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))), create


def gemini_client(*, response=None, error: Exception | None = None):
    generate_content = AsyncMock(return_value=response)
    generate_content.side_effect = error
    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content)), generate_content


def test_mock_provider_returns_normalized_response() -> None:
    response = run(MockProvider(response="safe mock").generate(REQUEST))
    assert response.provider == "mock" and response.text == "safe mock"


def test_provider_records_success_and_normalized_failure_metrics() -> None:
    metrics = AIMetricsRegistry()
    run(MockProvider(response="safe mock", metrics=metrics).generate(REQUEST))
    with pytest.raises(AiProviderError):
        run(MockProvider(failure_code=AiProviderErrorCode.TIMEOUT, metrics=metrics).generate(REQUEST))
    failure, success = metrics.snapshot()
    assert failure.key.error_code == "provider_timeout"
    assert success.key.outcome == "success"
    assert failure.call_count == success.call_count == 1


def test_provider_request_validation() -> None:
    with pytest.raises(InvalidInputError, match="must be minimized"):
        AiTextRequest(
            context=cast(MinimizedAIContext, "private prompt"),
            function="matter_summary",
            model="test-model",
            request_id="request-1",
            execution_id="a" * 32,
        )
    with pytest.raises(InvalidInputError, match="safe metric label"):
        AiTextRequest(
            context=REQUEST.context,
            function="Private matter text",
            model="test-model",
            request_id="request-1",
            execution_id="a" * 32,
        )


def test_provider_logs_correlated_lifecycle_without_content() -> None:
    logger = MagicMock(spec=logging.Logger)
    response = run(MockProvider(response="private response", logger=logger).generate(REQUEST))
    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert "ai_provider_started" in log_text and "ai_provider_succeeded" in log_text
    assert REQUEST.request_id in log_text and REQUEST.execution_id in log_text
    assert REQUEST.context.render_untrusted_data() not in log_text and response.text not in log_text


def test_openai_provider_uses_injected_official_client_without_leaking_key() -> None:
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=" result "))])
    client, create = openai_client(response=response)
    result = run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="fallback", client=client).generate(REQUEST))
    assert result.text == "result"
    kwargs = create.await_args.kwargs
    assert kwargs["model"] == REQUEST.model
    assert kwargs["messages"][0]["role"] == "system"
    assert "Summarize this" in kwargs["messages"][0]["content"]
    assert "Private matter" not in kwargs["messages"][0]["content"]
    assert kwargs["messages"][1]["content"] == REQUEST.context.render_untrusted_data()
    assert kwargs["tool_choice"] == "none" and "tools" not in kwargs
    assert PROVIDER_API_KEY not in repr(kwargs)


def test_gemini_provider_uses_injected_official_client_and_structured_config() -> None:
    request = AiTextRequest(
        context=REQUEST.context,
        function=REQUEST.function,
        model=REQUEST.model,
        request_id=REQUEST.request_id,
        execution_id=REQUEST.execution_id,
        response_json_schema={"type": "object", "properties": {"summary": {"type": "string"}}},
    )
    client, generate_content = gemini_client(response=SimpleNamespace(text=' {"summary":"resultado"} '))
    result = run(GeminiProvider(api_key=PROVIDER_API_KEY, model="fallback", client=client).generate(request))
    assert result.text == '{"summary":"resultado"}'
    kwargs = generate_content.await_args.kwargs
    assert kwargs["model"] == request.model
    assert kwargs["contents"].parts[0].text == request.context.render_untrusted_data()
    config = kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == request.response_json_schema
    assert config.tools == []
    assert "Summarize this" in str(config.system_instruction)
    assert "Private matter" not in str(config.system_instruction)
    assert PROVIDER_API_KEY not in repr(kwargs)


def test_gemini_provider_plain_text_config() -> None:
    client, generate_content = gemini_client(response=SimpleNamespace(text="gemini result"))
    response = run(GeminiProvider(api_key=PROVIDER_API_KEY, model="fallback", client=client).generate(REQUEST))
    assert response.text == "gemini result"
    assert generate_content.await_args.kwargs["config"].response_json_schema is None


@pytest.mark.parametrize("provider", [OpenAIProvider, GeminiProvider])
def test_empty_provider_key_is_rejected(provider) -> None:
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        provider(api_key=" ", model="test")


def test_default_official_clients_are_constructed(monkeypatch: pytest.MonkeyPatch) -> None:
    openai_sdk = MagicMock(return_value=SimpleNamespace())
    gemini_async = SimpleNamespace()
    google_sdk = MagicMock(return_value=SimpleNamespace(aio=gemini_async))
    monkeypatch.setattr(ai_providers.openai, "AsyncOpenAI", openai_sdk)
    monkeypatch.setattr(ai_providers.genai, "Client", google_sdk)
    assert OpenAIProvider(api_key=PROVIDER_API_KEY, model="test")._client is openai_sdk.return_value
    assert GeminiProvider(api_key=PROVIDER_API_KEY, model="test")._client is gemini_async
    openai_sdk.assert_called_once_with(api_key=PROVIDER_API_KEY, timeout=30, max_retries=0)
    google_sdk.assert_called_once_with(api_key=PROVIDER_API_KEY)


def test_official_model_lists_are_filtered_and_normalized() -> None:
    openai_list = AsyncMock(
        return_value=SimpleNamespace(
            data=[SimpleNamespace(id="gpt-text"), SimpleNamespace(id="gpt-audio"), SimpleNamespace(id="embedding-1")]
        )
    )
    openai_sdk = SimpleNamespace(models=SimpleNamespace(list=openai_list))

    class Pager:
        def __aiter__(self):
            return self

        async def __anext__(self):
            if hasattr(self, "done"):
                raise StopAsyncIteration
            self.done = True
            return SimpleNamespace(
                name="models/gemini-text", display_name="Gemini Text", supported_actions=["generateContent"]
            )

    gemini_list = AsyncMock(return_value=Pager())
    gemini_sdk = SimpleNamespace(models=SimpleNamespace(list=gemini_list))

    assert [item.id for item in run(list_openai_models(api_key=PROVIDER_API_KEY, client=openai_sdk))] == ["gpt-text"]
    assert [item.id for item in run(list_gemini_models(api_key=PROVIDER_API_KEY, client=gemini_sdk))] == ["gemini-text"]


@pytest.mark.parametrize(
    ("function", "client"),
    [
        (
            list_openai_models,
            SimpleNamespace(models=SimpleNamespace(list=AsyncMock(side_effect=RuntimeError("secret")))),
        ),
        (
            list_gemini_models,
            SimpleNamespace(models=SimpleNamespace(list=AsyncMock(side_effect=RuntimeError("secret")))),
        ),
    ],
)
def test_model_list_failures_are_safe(function, client) -> None:
    with pytest.raises(AiProviderError, match="no est") as captured:
        run(function(api_key=PROVIDER_API_KEY, client=client))
    assert "secret" not in str(captured.value)


def _openai_status_error(status: int) -> openai.APIStatusError:
    request = httpx.Request("POST", "https://provider.invalid")
    response = httpx.Response(status, request=request)
    if status == 401:
        return openai.AuthenticationError("private", response=response, body=None)
    if status == 429:
        return openai.RateLimitError("private", response=response, body=None)
    return openai.APIStatusError("private", response=response, body=None)


@pytest.mark.parametrize(
    ("external_error", "expected"),
    [
        (
            openai.APITimeoutError(request=httpx.Request("POST", "https://provider.invalid")),
            AiProviderErrorCode.TIMEOUT,
        ),
        (_openai_status_error(401), AiProviderErrorCode.AUTHENTICATION_FAILED),
        (_openai_status_error(429), AiProviderErrorCode.RATE_LIMITED),
        (_openai_status_error(408), AiProviderErrorCode.TIMEOUT),
        (_openai_status_error(503), AiProviderErrorCode.UNAVAILABLE),
        (_openai_status_error(400), AiProviderErrorCode.REQUEST_REJECTED),
        (
            openai.APIConnectionError(request=httpx.Request("POST", "https://provider.invalid")),
            AiProviderErrorCode.UNAVAILABLE,
        ),
    ],
)
def test_openai_sdk_errors_map_to_safe_taxonomy(external_error: Exception, expected: AiProviderErrorCode) -> None:
    client, _ = openai_client(error=external_error)
    with pytest.raises(AiProviderError) as captured:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", client=client).generate(REQUEST))
    assert captured.value.code is expected
    assert "private" not in str(captured.value) and PROVIDER_API_KEY not in str(captured.value)


@pytest.mark.parametrize(
    ("external_error", "expected"),
    [
        (genai_errors.APIError(401, {"error": "private"}), AiProviderErrorCode.AUTHENTICATION_FAILED),
        (genai_errors.APIError(429, {"error": "private"}), AiProviderErrorCode.RATE_LIMITED),
        (genai_errors.APIError(504, {"error": "private"}), AiProviderErrorCode.TIMEOUT),
        (genai_errors.APIError(503, {"error": "private"}), AiProviderErrorCode.UNAVAILABLE),
        (genai_errors.APIError(400, {"error": "private"}), AiProviderErrorCode.REQUEST_REJECTED),
        (TimeoutError("private"), AiProviderErrorCode.TIMEOUT),
        (RuntimeError("private"), AiProviderErrorCode.UNAVAILABLE),
    ],
)
def test_gemini_sdk_errors_map_to_safe_taxonomy(external_error: Exception, expected: AiProviderErrorCode) -> None:
    client, _ = gemini_client(error=external_error)
    with pytest.raises(AiProviderError) as captured:
        run(GeminiProvider(api_key=PROVIDER_API_KEY, model="test", client=client).generate(REQUEST))
    assert captured.value.code is expected
    assert "private" not in str(captured.value) and PROVIDER_API_KEY not in str(captured.value)


@pytest.mark.parametrize(
    "response",
    [SimpleNamespace(choices=[]), SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=" "))])],
)
def test_openai_invalid_sdk_response_is_rejected(response) -> None:
    client, _ = openai_client(response=response)
    with pytest.raises(AiProviderError) as captured:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", client=client).generate(REQUEST))
    assert captured.value.code is AiProviderErrorCode.INVALID_RESPONSE


@pytest.mark.parametrize("response", [object(), SimpleNamespace(text=None), SimpleNamespace(text=" ")])
def test_gemini_invalid_sdk_response_is_rejected(response) -> None:
    client, _ = gemini_client(response=response)
    with pytest.raises(AiProviderError) as captured:
        run(GeminiProvider(api_key=PROVIDER_API_KEY, model="test", client=client).generate(REQUEST))
    assert captured.value.code is AiProviderErrorCode.INVALID_RESPONSE


def test_provider_observer_logs_unexpected_error_type_without_message() -> None:
    logger = MagicMock(spec=logging.Logger)
    provider = MockProvider(logger=logger)

    async def unexpected() -> str:
        raise RuntimeError("private unexpected detail")

    with pytest.raises(RuntimeError, match="private unexpected detail"):
        run(provider._observe(REQUEST, model=REQUEST.model, operation=unexpected))
    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert "RuntimeError" in log_text and "private unexpected detail" not in log_text


@pytest.mark.parametrize("code", list(AiProviderErrorCode))
def test_mock_provider_uses_same_public_failure_contract(code: AiProviderErrorCode) -> None:
    with pytest.raises(AiProviderError) as error:
        run(MockProvider(failure_code=code).generate(REQUEST))
    failure = error.value.to_public_failure()
    assert failure.code == code.value and failure.retryable is error.value.retryable
    assert PROVIDER_API_KEY not in repr(failure)
