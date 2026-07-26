"""Provider-neutral contracts and safe adapters for text-generation providers."""

import asyncio
import json
import logging
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from app.core.common.ai_metrics import AI_METRICS, AIMetricsRegistry
from app.core.common.observability import AiCorrelationContext, log_ai_event
from app.core.errors.services import InvalidInputError
from app.integrations.ai_context import UNTRUSTED_DATA_POLICY, MinimizedAIContext


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
    context: MinimizedAIContext
    function: str
    model: str
    request_id: str
    execution_id: str
    max_tokens: int = 512

    def __post_init__(self) -> None:
        if not isinstance(self.context, MinimizedAIContext):
            raise InvalidInputError("AI provider context must be minimized")
        if re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", self.function) is None:
            raise InvalidInputError("AI function is not a safe metric label")


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


class _ObservedAiProvider:
    provider: str

    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        metrics: AIMetricsRegistry | None = None,
    ):
        self._logger = logger or logging.getLogger("app.ai_provider")
        self._metrics = metrics or AI_METRICS

    async def _observe(
        self,
        request: AiTextRequest,
        *,
        model: str,
        operation: Callable[[], Awaitable[str]],
    ) -> AiTextResponse:
        correlation = AiCorrelationContext(
            request_id=request.request_id,
            execution_id=request.execution_id,
        )
        started_at = perf_counter()
        log_ai_event(
            self._logger,
            layer="ai_provider",
            event="ai_provider_started",
            correlation=correlation,
            provider=self.provider,
            model=model,
        )
        try:
            text = await operation()
        except AiProviderError as exc:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            self._metrics.record(
                provider=self.provider,
                function=request.function,
                outcome="failure",
                error_code=exc.error_code,
                duration_ms=duration_ms,
            )
            log_ai_event(
                self._logger,
                layer="ai_provider",
                event="ai_provider_failed",
                correlation=correlation,
                provider=self.provider,
                model=model,
                error_code=exc.error_code,
                retryable=exc.retryable,
                duration_ms=duration_ms,
                level=logging.WARNING,
            )
            raise
        except Exception as exc:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            self._metrics.record(
                provider=self.provider,
                function=request.function,
                outcome="failure",
                error_code="internal_error",
                duration_ms=duration_ms,
            )
            log_ai_event(
                self._logger,
                layer="ai_provider",
                event="ai_provider_failed",
                correlation=correlation,
                provider=self.provider,
                model=model,
                error_type=type(exc).__name__,
                duration_ms=duration_ms,
                level=logging.ERROR,
            )
            raise
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        self._metrics.record(
            provider=self.provider,
            function=request.function,
            outcome="success",
            duration_ms=duration_ms,
        )
        log_ai_event(
            self._logger,
            layer="ai_provider",
            event="ai_provider_succeeded",
            correlation=correlation,
            provider=self.provider,
            model=model,
            duration_ms=duration_ms,
        )
        return AiTextResponse(provider=self.provider, model=model, text=text)


class _HttpAiProvider(_ObservedAiProvider):
    provider: str

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        transport: JsonTransport | None = None,
        logger: logging.Logger | None = None,
        metrics: AIMetricsRegistry | None = None,
    ):
        super().__init__(logger=logger, metrics=metrics)
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

        async def execute() -> str:
            payload = await self._post(
                url="https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                body={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": f"{UNTRUSTED_DATA_POLICY}\n\n{request.context.instruction}",
                        },
                        {
                            "role": "user",
                            "content": request.context.render_untrusted_data(),
                        },
                    ],
                    "max_tokens": request.max_tokens,
                    "tool_choice": "none",
                },
            )
            return _require_text(payload, "choices.0.message.content") if isinstance(payload, Mapping) else ""

        return await self._observe(request, model=model, operation=execute)


class GeminiProvider(_HttpAiProvider):
    provider = "gemini"

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        model = request.model or self._model

        async def execute() -> str:
            payload = await self._post(
                url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"Content-Type": "application/json", "x-goog-api-key": self._api_key},
                body={
                    "systemInstruction": {
                        "parts": [
                            {
                                "text": f"{UNTRUSTED_DATA_POLICY}\n\n{request.context.instruction}",
                            }
                        ]
                    },
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": request.context.render_untrusted_data()}],
                        }
                    ],
                    "generationConfig": {"maxOutputTokens": request.max_tokens},
                },
            )
            return _require_text(payload, "candidates.0.content.parts.0.text") if isinstance(payload, Mapping) else ""

        return await self._observe(request, model=model, operation=execute)


class MockProvider(_ObservedAiProvider):
    provider = "mock"

    def __init__(
        self,
        *,
        response: str = "Mock AI response",
        model: str = "mock-model",
        failure_code: AiProviderErrorCode | None = None,
        logger: logging.Logger | None = None,
        metrics: AIMetricsRegistry | None = None,
    ):
        super().__init__(logger=logger, metrics=metrics)
        self._response = response
        self._model = model
        self._failure_code = failure_code

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        model = request.model or self._model

        async def execute() -> str:
            if self._failure_code is not None:
                raise AiProviderError(self._failure_code)
            return self._response

        return await self._observe(request, model=model, operation=execute)
