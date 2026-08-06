"""Provider-neutral contracts and safe adapters for text-generation providers."""

import logging
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter
from typing import Any, Protocol, cast

import openai
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

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
    response_json_schema: Mapping[str, Any] | None = None

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


@dataclass(frozen=True)
class AiModel:
    """Provider-neutral model available to the current BYOK credential."""

    id: str
    label: str


async def list_openai_models(*, api_key: str, client: Any | None = None) -> list[AiModel]:
    sdk = client or openai.AsyncOpenAI(api_key=api_key, timeout=30, max_retries=0)
    try:
        response = await sdk.models.list()
    except Exception as exc:
        raise _map_openai_error(exc) from exc
    models = []
    for item in response.data:
        model_id = getattr(item, "id", "")
        lowered = model_id.lower()
        if (
            isinstance(model_id, str)
            and model_id.startswith("gpt-")
            and not any(marker in lowered for marker in ("audio", "image", "realtime", "transcribe", "tts"))
        ):
            models.append(AiModel(id=model_id, label=model_id))
    return sorted(models, key=lambda item: item.id)


async def list_gemini_models(*, api_key: str, client: Any | None = None) -> list[AiModel]:
    sdk = cast(genai.client.AsyncClient, client) if client is not None else genai.Client(api_key=api_key).aio
    try:
        pager = await sdk.models.list()
        items = [item async for item in pager]
    except Exception as exc:
        raise _map_gemini_error(exc) from exc
    models = []
    for item in items:
        actions = getattr(item, "supported_actions", None) or []
        name = getattr(item, "name", "")
        if isinstance(name, str) and name.startswith("models/gemini") and "generateContent" in actions:
            model_id = name.removeprefix("models/")
            label = getattr(item, "display_name", None) or model_id
            models.append(AiModel(id=model_id, label=label))
    return sorted(models, key=lambda item: item.id)


def _require_openai_text(response: Any) -> str:
    try:
        text = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE) from exc
    if not isinstance(text, str) or not text.strip():
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE)
    return text.strip()


def _require_gemini_text(response: Any) -> str:
    """Return SDK-normalized text while rejecting empty or malformed responses."""
    try:
        text = response.text
    except (AttributeError, ValueError) as exc:
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE) from exc
    if not isinstance(text, str) or not text.strip():
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE)
    return text.strip()


def _status_error_code(status: int) -> AiProviderErrorCode:
    if status in {401, 403}:
        return AiProviderErrorCode.AUTHENTICATION_FAILED
    if status == 429:
        return AiProviderErrorCode.RATE_LIMITED
    if status in {408, 504}:
        return AiProviderErrorCode.TIMEOUT
    if status >= 500 or status < 100:
        return AiProviderErrorCode.UNAVAILABLE
    return AiProviderErrorCode.REQUEST_REJECTED


def _map_openai_error(exc: Exception) -> AiProviderError:
    if isinstance(exc, openai.APITimeoutError):
        return AiProviderError(AiProviderErrorCode.TIMEOUT)
    if isinstance(exc, openai.AuthenticationError):
        return AiProviderError(AiProviderErrorCode.AUTHENTICATION_FAILED)
    if isinstance(exc, openai.RateLimitError):
        return AiProviderError(AiProviderErrorCode.RATE_LIMITED)
    if isinstance(exc, openai.APIStatusError):
        return AiProviderError(_status_error_code(exc.status_code))
    return AiProviderError(AiProviderErrorCode.UNAVAILABLE)


def _map_gemini_error(exc: Exception) -> AiProviderError:
    if isinstance(exc, genai_errors.APIError):
        return AiProviderError(_status_error_code(exc.code))
    if isinstance(exc, TimeoutError):
        return AiProviderError(AiProviderErrorCode.TIMEOUT)
    return AiProviderError(AiProviderErrorCode.UNAVAILABLE)


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


class OpenAIProvider(_ObservedAiProvider):
    provider = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        client: Any | None = None,
        logger: logging.Logger | None = None,
        metrics: AIMetricsRegistry | None = None,
    ):
        super().__init__(logger=logger, metrics=metrics)
        if not api_key.strip():
            raise ValueError("api_key cannot be empty")
        self._model = model
        self._client = client or openai.AsyncOpenAI(api_key=api_key, timeout=30, max_retries=0)

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        model = request.model or self._model

        async def execute() -> str:
            try:
                response = await self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"{UNTRUSTED_DATA_POLICY}\n\n{request.context.instruction}",
                        },
                        {
                            "role": "user",
                            "content": request.context.render_untrusted_data(),
                        },
                    ],
                    max_tokens=request.max_tokens,
                    tool_choice="none",
                )
            except Exception as exc:
                raise _map_openai_error(exc) from exc
            return _require_openai_text(response)

        return await self._observe(request, model=model, operation=execute)


class GeminiProvider(_ObservedAiProvider):
    provider = "gemini"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        client: Any | None = None,
        logger: logging.Logger | None = None,
        metrics: AIMetricsRegistry | None = None,
    ):
        super().__init__(logger=logger, metrics=metrics)
        if not api_key.strip():
            raise ValueError("api_key cannot be empty")
        self._model = model
        self._client = client or genai.Client(api_key=api_key).aio

    async def generate(self, request: AiTextRequest) -> AiTextResponse:
        model = request.model or self._model

        async def execute() -> str:
            config: dict[str, Any] = {
                "max_output_tokens": request.max_tokens,
                "system_instruction": f"{UNTRUSTED_DATA_POLICY}\n\n{request.context.instruction}",
                "tools": [],
            }
            if request.response_json_schema is not None:
                config.update(
                    {
                        "response_mime_type": "application/json",
                        "response_json_schema": dict(request.response_json_schema),
                    }
                )
            try:
                response = await self._client.models.generate_content(
                    model=model,
                    contents=genai_types.Content(
                        role="user",
                        parts=[genai_types.Part(text=request.context.render_untrusted_data())],
                    ),
                    config=genai_types.GenerateContentConfig(**config),
                )
            except Exception as exc:
                raise _map_gemini_error(exc) from exc
            return _require_gemini_text(response)

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
