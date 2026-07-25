import asyncio
from io import BytesIO

import pytest

from app.integrations import ai_providers
from app.integrations.ai_providers import (
    AiProviderError,
    AiTextRequest,
    GeminiProvider,
    MockProvider,
    OpenAIProvider,
)

REQUEST = AiTextRequest(prompt="Summarize this", model="test-model")
PROVIDER_API_KEY = "provider-secret"  # pragma: allowlist secret


def run(coroutine):
    return asyncio.run(coroutine)


def test_mock_provider_returns_normalized_response() -> None:
    response = run(MockProvider(response="safe mock").generate(REQUEST))
    assert response.provider == "mock"
    assert response.text == "safe mock"


def test_openai_provider_builds_provider_payload_without_leaking_key() -> None:
    calls = []

    async def transport(url, headers, body):
        calls.append((url, headers, body))
        return 200, {"choices": [{"message": {"content": "result"}}]}

    response = run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="fallback", transport=transport).generate(REQUEST))
    assert response.text == "result"
    assert calls[0][0].endswith("/chat/completions")
    assert b"Summarize this" in calls[0][2]
    assert calls[0][1]["Authorization"] == f"Bearer {PROVIDER_API_KEY}"


def test_gemini_provider_normalizes_response() -> None:
    async def transport(url, headers, body):
        assert f":generateContent?key={PROVIDER_API_KEY}" in url
        return 200, {"candidates": [{"content": {"parts": [{"text": "gemini result"}]}}]}

    response = run(GeminiProvider(api_key=PROVIDER_API_KEY, model="gemini-test", transport=transport).generate(REQUEST))
    assert response.provider == "gemini"
    assert response.text == "gemini result"


def test_provider_failures_are_safe_and_retryable() -> None:
    async def transport(url, headers, body):
        return 503, {"error": "contains provider details"}

    with pytest.raises(AiProviderError, match="AI provider request failed") as error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=transport).generate(REQUEST))
    assert error.value.retryable is True
    assert PROVIDER_API_KEY not in str(error.value)


def test_invalid_provider_response_is_rejected() -> None:
    async def transport(url, headers, body):
        return 200, {"choices": []}

    with pytest.raises(AiProviderError, match="invalid response"):
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=transport).generate(REQUEST))


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
    assert error.value.retryable is True

    monkeypatch.setattr(ai_providers, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad json")))
    with pytest.raises(AiProviderError):
        run(ai_providers._default_transport("https://provider.test", {}, b"{}"))


def test_provider_maps_non_retryable_status_and_transport_errors() -> None:
    async def bad_status(url, headers, body):
        return 400, None

    with pytest.raises(AiProviderError) as status_error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=bad_status).generate(REQUEST))
    assert status_error.value.retryable is False

    async def unexpected_error(url, headers, body):
        raise RuntimeError("provider internals")

    with pytest.raises(AiProviderError) as transport_error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=unexpected_error).generate(REQUEST))
    assert transport_error.value.retryable is True


def test_provider_rethrows_safe_provider_error() -> None:
    async def provider_error(url, headers, body):
        raise AiProviderError(retryable=False)

    with pytest.raises(AiProviderError) as error:
        run(OpenAIProvider(api_key=PROVIDER_API_KEY, model="test", transport=provider_error).generate(REQUEST))
    assert error.value.retryable is False


def test_response_text_parser_rejects_wrong_shape_and_blank_text() -> None:
    with pytest.raises(AiProviderError, match="invalid response"):
        ai_providers._require_text("not-an-object", "value")
    with pytest.raises(AiProviderError, match="invalid response"):
        ai_providers._require_text({"value": "  "}, "value")
