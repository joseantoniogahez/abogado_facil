"""Provider-neutral contracts and safe adapters for text-generation providers."""

import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class AiProviderErrorCode(StrEnum):
    """Provider-neutral codes safe to persist and expose to API consumers."""

    AUTHENTICATION_FAILED = "provider_authentication_failed"
    RATE_LIMITED = "provider_rate_limited"
    TIMEOUT = "provider_timeout"
    UNAVAILABLE = "provider_unavailable"
    REQUEST_REJECTED = "provider_request_rejected"
    INVALID_RESPONSE = "provider_invalid_response"
    CONFIGURATION_ERROR = "provider_configuration_error"


@dataclass(frozen=True)
class AiProviderFailure:
    """Public failure contract without provider-controlled values."""

    code: str
    message: str
    retryable: bool


_ERROR_POLICY: dict[AiProviderErrorCode, tuple[str, bool]] = {
    AiProviderErrorCode.AUTHENTICATION_FAILED: ("Revisa la credencial y el acceso del proveedor de IA.", False),
    AiProviderErrorCode.RATE_LIMITED: ("El proveedor de IA alcanzó temporalmente su límite.", True),
    AiProviderErrorCode.TIMEOUT: ("El proveedor de IA tardó demasiado en responder.", True),
    AiProviderErrorCode.UNAVAILABLE: ("El proveedor de IA no está disponible temporalmente.", True),
    AiProviderErrorCode.REQUEST_REJECTED: ("El proveedor de IA rechazó la solicitud.", False),
    AiProviderErrorCode.INVALID_RESPONSE: ("El proveedor de IA devolvió una respuesta inválida.", False),
    AiProviderErrorCode.CONFIGURATION_ERROR: ("La configuración del proveedor de IA no es válida.", False),
}


class AiProviderError(Exception):
    """Safe, classified provider failure without external response details."""

    def __init__(self, code: AiProviderErrorCode):
        message, retryable = _ERROR_POLICY[code]
        super().__init__(message)
        self.code = code
        self.retryable = retryable

    @property
    def error_code(self) -> str:
        """Return the stable value accepted by ``AIJob.error_code``."""
        return self.code.value

    def to_public_failure(self) -> AiProviderFailure:
        return AiProviderFailure(code=self.error_code, message=str(self), retryable=self.retryable)


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


def _validate_provider_url(url: str) -> None:
    try:
        parsed_url = urlsplit(url)
    except ValueError as exc:
        raise AiProviderError(AiProviderErrorCode.CONFIGURATION_ERROR) from exc
    if parsed_url.scheme != "https" or parsed_url.hostname is None:
        raise AiProviderError(AiProviderErrorCode.CONFIGURATION_ERROR)


def _default_transport(url: str, headers: Mapping[str, str], body: bytes) -> Awaitable[tuple[int, Any]]:
    async def send() -> tuple[int, Any]:
        def request() -> tuple[int, Any]:
            _validate_provider_url(url)
            try:
                response_request = Request(url, data=body, headers=dict(headers), method="POST")
                with urlopen(response_request, timeout=30) as response:  # nosec B310 - HTTPS validated above.
                    return response.status, json.loads(response.read())
            except HTTPError as exc:
                return exc.code, None
            except TimeoutError as exc:
                raise AiProviderError(AiProviderErrorCode.TIMEOUT) from exc
            except URLError as exc:
                code = (
                    AiProviderErrorCode.TIMEOUT
                    if isinstance(exc.reason, TimeoutError)
                    else AiProviderErrorCode.UNAVAILABLE
                )
                raise AiProviderError(code) from exc
            except ValueError as exc:
                raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE) from exc

        return await asyncio.to_thread(request)

    return send()


def _require_text(payload: Any, path: str) -> str:
    value: Any = payload
    for key in path.split("."):
        if isinstance(value, list) and key.isdigit():
            try:
                value = value[int(key)]
            except IndexError as exc:
                raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE) from exc
        elif isinstance(value, Mapping):
            value = value.get(key)
        else:
            raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE)
    if not isinstance(value, str) or not value.strip():
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE)
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
        except TimeoutError as exc:
            raise AiProviderError(AiProviderErrorCode.TIMEOUT) from exc
        except Exception as exc:
            raise AiProviderError(AiProviderErrorCode.UNAVAILABLE) from exc
        if status in {401, 403}:
            raise AiProviderError(AiProviderErrorCode.AUTHENTICATION_FAILED)
        if status == 429:
            raise AiProviderError(AiProviderErrorCode.RATE_LIMITED)
        if status in {408, 504}:
            raise AiProviderError(AiProviderErrorCode.TIMEOUT)
        if status >= 500 or status < 100:
            raise AiProviderError(AiProviderErrorCode.UNAVAILABLE)
        if status < 200 or status >= 300:
            raise AiProviderError(AiProviderErrorCode.REQUEST_REJECTED)
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
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"Content-Type": "application/json", "x-goog-api-key": self._api_key},
            body={
                "contents": [{"parts": [{"text": request.prompt}]}],
                "generationConfig": {"maxOutputTokens": request.max_tokens},
            },
        )
        text = _require_text(payload, "candidates.0.content.parts.0.text") if isinstance(payload, Mapping) else ""
        return AiTextResponse(provider=self.provider, model=model, text=text)


class MockProvider:
    provider = "mock"

    def __init__(
        self,
        *,
        response: str = "Mock AI response",
        model: str = "mock-model",
        failure_code: AiProviderErrorCode | None = None,
    ):
        self._response = response
        self._model = model
        self._failure_code = failure_code

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        if self._failure_code is not None:
            raise AiProviderError(self._failure_code)
        return AiTextResponse(provider=self.provider, model=request.model or self._model, text=self._response)
