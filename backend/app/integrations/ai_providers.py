"""Provider-neutral contracts and safe adapters for text-generation providers."""

import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AiProviderError(Exception):
    """Safe provider failure that never carries credentials or response bodies."""

    def __init__(self, message: str = "AI provider request failed", *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


@dataclass(frozen=True)
class AiTextRequest:
    prompt: str
    model: str
    max_tokens: int = 512


@dataclass(frozen=True)
class AiTextResponse:
    provider: str
    model: str
    text: str


class AiProviderPort(Protocol):
    provider: str

    async def generate(self, request: AiTextRequest) -> AiTextResponse: ...


JsonTransport = Callable[[str, Mapping[str, str], bytes], Awaitable[tuple[int, Any]]]


def _default_transport(url: str, headers: Mapping[str, str], body: bytes) -> Awaitable[tuple[int, Any]]:
    async def send() -> tuple[int, Any]:
        def request() -> tuple[int, Any]:
            try:
                response_request = Request(url, data=body, headers=dict(headers), method="POST")
                with urlopen(response_request, timeout=30) as response:  # noqa: S310 - URL is provider configuration.
                    return response.status, json.loads(response.read())
            except HTTPError as exc:
                return exc.code, None
            except (URLError, TimeoutError, ValueError) as exc:
                raise AiProviderError(retryable=True) from exc

        return await asyncio.to_thread(request)

    return send()


def _require_text(payload: Any, path: str) -> str:
    value: Any = payload
    for key in path.split("."):
        if isinstance(value, list) and key.isdigit():
            try:
                value = value[int(key)]
            except IndexError as exc:
                raise AiProviderError("AI provider returned an invalid response") from exc
        elif isinstance(value, Mapping):
            value = value.get(key)
        else:
            raise AiProviderError("AI provider returned an invalid response")
    if not isinstance(value, str) or not value.strip():
        raise AiProviderError("AI provider returned an invalid response")
    return value.strip()


class _HttpAiProvider:
    provider: str

    def __init__(self, *, api_key: str, model: str, transport: JsonTransport | None = None):
        if not api_key.strip():
            raise ValueError("api_key cannot be empty")
        self._api_key = api_key
        self._model = model
        self._transport = transport or _default_transport

    async def _post(self, *, url: str, headers: Mapping[str, str], body: dict[str, Any]) -> Any:
        try:
            status, payload = await self._transport(url, headers, json.dumps(body).encode("utf-8"))
        except AiProviderError:
            raise
        except Exception as exc:
            raise AiProviderError(retryable=True) from exc
        if status == 429 or status >= 500:
            raise AiProviderError(retryable=True)
        if status < 200 or status >= 300:
            raise AiProviderError()
        return payload


class OpenAIProvider(_HttpAiProvider):
    provider = "openai"

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        model = request.model or self._model
        payload = await self._post(
            url="https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            body={
                "model": model,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens,
            },
        )
        text = _require_text(payload, "choices.0.message.content") if isinstance(payload, Mapping) else ""
        return AiTextResponse(provider=self.provider, model=model, text=text)


class GeminiProvider(_HttpAiProvider):
    provider = "gemini"

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        model = request.model or self._model
        payload = await self._post(
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self._api_key}",
            headers={"Content-Type": "application/json"},
            body={
                "contents": [{"parts": [{"text": request.prompt}]}],
                "generationConfig": {"maxOutputTokens": request.max_tokens},
            },
        )
        text = _require_text(payload, "candidates.0.content.parts.0.text") if isinstance(payload, Mapping) else ""
        return AiTextResponse(provider=self.provider, model=model, text=text)


class MockProvider:
    provider = "mock"

    def __init__(self, *, response: str = "Mock AI response", model: str = "mock-model"):
        self._response = response
        self._model = model

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        return AiTextResponse(provider=self.provider, model=request.model or self._model, text=self._response)
