"""Cross-provider contract tests for the supported AI adapters."""

import asyncio
import logging
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.integrations.ai_context import build_minimized_ai_context
from app.integrations.ai_providers import (
    AiProviderError,
    AiProviderErrorCode,
    AiProviderPort,
    AiTextRequest,
    GeminiProvider,
    MockProvider,
    OpenAIProvider,
)

API_KEY = "contract-provider-secret"  # pragma: allowlist secret
EXTERNAL_DETAIL = "private provider payload"
REQUEST = AiTextRequest(
    context=build_minimized_ai_context(
        instruction="Analyze the authorized legal context",
        source_context={"legal_context": "private legal prompt"},
        authorized_fields={"legal_context"},
        necessary_fields={"legal_context"},
    ),
    function="legal_analysis",
    model="contract-model",
    request_id="request-contract",
    execution_id="c" * 32,
)
ProviderFactory = Callable[[str, MagicMock], AiProviderPort]


def run(coroutine):
    return asyncio.run(coroutine)


def _openai_factory(scenario: str, logger: MagicMock) -> OpenAIProvider:
    async def transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, Any]:
        outcomes = {
            "success": (200, {"choices": [{"message": {"content": "normalized result"}}]}),
            "timeout": (504, {"error": EXTERNAL_DETAIL}),
            "rate_limit": (429, {"error": EXTERNAL_DETAIL}),
            "invalid_response": (200, {"choices": []}),
        }
        return outcomes[scenario]

    return OpenAIProvider(api_key=API_KEY, model=REQUEST.model, transport=transport, logger=logger)


def _gemini_factory(scenario: str, logger: MagicMock) -> GeminiProvider:
    async def transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, Any]:
        outcomes = {
            "success": (
                200,
                {"candidates": [{"content": {"parts": [{"text": "normalized result"}]}}]},
            ),
            "timeout": (504, {"error": EXTERNAL_DETAIL}),
            "rate_limit": (429, {"error": EXTERNAL_DETAIL}),
            "invalid_response": (200, {"candidates": []}),
        }
        return outcomes[scenario]

    return GeminiProvider(api_key=API_KEY, model=REQUEST.model, transport=transport, logger=logger)


def _mock_factory(scenario: str, logger: MagicMock) -> MockProvider:
    failures = {
        "timeout": AiProviderErrorCode.TIMEOUT,
        "rate_limit": AiProviderErrorCode.RATE_LIMITED,
        "invalid_response": AiProviderErrorCode.INVALID_RESPONSE,
    }
    return MockProvider(
        response="normalized result",
        failure_code=failures.get(scenario),
        logger=logger,
    )


PROVIDERS: tuple[tuple[str, ProviderFactory], ...] = (
    ("openai", _openai_factory),
    ("gemini", _gemini_factory),
    ("mock", _mock_factory),
)


@pytest.mark.parametrize(("provider_name", "factory"), PROVIDERS)
def test_providers_share_success_contract(provider_name: str, factory: ProviderFactory) -> None:
    logger = MagicMock(spec=logging.Logger)

    response = run(factory("success", logger).generate(REQUEST))

    assert response.provider == provider_name
    assert response.model == REQUEST.model
    assert response.text == "normalized result"
    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert REQUEST.request_id in log_text
    assert REQUEST.execution_id in log_text
    assert REQUEST.context.render() not in log_text
    assert response.text not in log_text
    assert API_KEY not in log_text


@pytest.mark.parametrize(("provider_name", "factory"), PROVIDERS)
@pytest.mark.parametrize(
    ("scenario", "expected_code", "expected_retryable"),
    (
        ("timeout", AiProviderErrorCode.TIMEOUT, True),
        ("rate_limit", AiProviderErrorCode.RATE_LIMITED, True),
        ("invalid_response", AiProviderErrorCode.INVALID_RESPONSE, False),
    ),
)
def test_providers_share_safe_failure_and_retry_contract(
    provider_name: str,
    factory: ProviderFactory,
    scenario: str,
    expected_code: AiProviderErrorCode,
    expected_retryable: bool,
) -> None:
    logger = MagicMock(spec=logging.Logger)

    with pytest.raises(AiProviderError) as captured:
        run(factory(scenario, logger).generate(REQUEST))

    failure = captured.value.to_public_failure()
    assert failure.code == expected_code.value
    assert failure.retryable is expected_retryable
    assert provider_name not in failure.message.lower()
    assert EXTERNAL_DETAIL not in failure.message
    assert API_KEY not in failure.message

    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert expected_code.value in log_text
    assert REQUEST.request_id in log_text
    assert REQUEST.execution_id in log_text
    assert REQUEST.context.render() not in log_text
    assert EXTERNAL_DETAIL not in log_text
    assert API_KEY not in log_text


@pytest.mark.parametrize(("provider_name", "factory"), PROVIDERS)
def test_handler_contract_hands_only_recoverable_failures_to_rq(
    provider_name: str,
    factory: ProviderFactory,
) -> None:
    retryable_failures: list[AiProviderError] = []

    async def execute(scenario: str) -> None:
        try:
            await factory(scenario, MagicMock(spec=logging.Logger)).generate(REQUEST)
        except AiProviderError as error:
            if error.retryable:
                retryable_failures.append(error)
                raise
            return

    with pytest.raises(AiProviderError) as timeout:
        run(execute("timeout"))
    assert timeout.value.code is AiProviderErrorCode.TIMEOUT

    with pytest.raises(AiProviderError) as rate_limit:
        run(execute("rate_limit"))
    assert rate_limit.value.code is AiProviderErrorCode.RATE_LIMITED

    assert run(execute("invalid_response")) is None
    assert [error.code for error in retryable_failures] == [
        AiProviderErrorCode.TIMEOUT,
        AiProviderErrorCode.RATE_LIMITED,
    ]
