import asyncio
from functools import wraps
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors.domain import DomainError, DomainErrorType, ErrorLayer
from app.features.ai_assistance.repository import AIAssistanceRepository
from app.features.ai_assistance.router import (
    AI_PROVIDER_RETRY_AFTER_SECONDS,
    _firm_id,
    convert_result,
    execute_assistance,
    list_results,
    preview_context,
    review_result,
)
from app.features.ai_assistance.schemas import (
    AIContextPreviewRequest,
    ConvertAIAssistanceRequest,
    ExecuteAIAssistanceRequest,
    ReviewAIAssistanceRequest,
)
from app.features.ai_assistance.service import AIAssistanceService
from app.features.auth.principal import CurrentPrincipal
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode


def run_async(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))

    return wrapper


class Scalars:
    def __init__(self, values):
        self.values = values

    def scalar_one_or_none(self):
        return self.values[0] if self.values else None

    def scalars(self):
        return self

    def all(self):
        return self.values


@run_async
async def test_repository_scoped_operations() -> None:
    row = SimpleNamespace(id=1)
    session = SimpleNamespace(
        execute=AsyncMock(side_effect=[Scalars([row]), Scalars([row])]),
        scalar=AsyncMock(return_value=1),
        flush=AsyncMock(),
        refresh=AsyncMock(),
    )
    repository = AIAssistanceRepository(cast(AsyncSession, session))
    assert await repository.get_scoped(result_id=1, matter_id=2, firm_id=3) is row
    assert await repository.list_scoped(matter_id=2, firm_id=3) == [row]
    assert await repository.count_scoped(matter_id=2, firm_id=3) == 1
    assert await repository.update_result(row, review_status="accepted") is row
    assert row.review_status == "accepted"


@run_async
async def test_router_functions_delegate_scoped_identity() -> None:
    user = cast(CurrentPrincipal, SimpleNamespace(id=4, firm_id=3))
    service = cast(
        AIAssistanceService,
        SimpleNamespace(
            preview=AsyncMock(return_value="preview"),
            execute=AsyncMock(return_value="executed"),
            list=AsyncMock(return_value=([], 0)),
            review=AsyncMock(return_value="reviewed"),
            convert=AsyncMock(return_value="converted"),
        ),
    )
    preview_payload = AIContextPreviewRequest(
        feature="intake_analysis",
        narrative="Relato suficientemente largo.",
        provider="openai",
        model="model",
    )
    execute_payload = ExecuteAIAssistanceRequest(**preview_payload.model_dump(), confirmation_token="a" * 64)
    assert await preview_context(2, preview_payload, user, service) == "preview"
    request = cast(Request, SimpleNamespace(state=SimpleNamespace(request_id="req")))
    assert await execute_assistance(2, execute_payload, request, user, service) == "executed"
    listed = await list_results(2, user, service)
    assert listed.total == 0
    review_payload = ReviewAIAssistanceRequest(status="rejected")
    assert await review_result(2, 8, review_payload, user, service) == "reviewed"
    action = ConvertAIAssistanceRequest(action_type="note", content="text")
    assert await convert_result(2, 8, action, user, service) == "converted"
    assert _firm_id(user) == 3
    with pytest.raises(ValueError):
        _firm_id(cast(CurrentPrincipal, SimpleNamespace(firm_id=None)))


@run_async
async def test_execute_maps_provider_rate_limit_to_normalized_http_error() -> None:
    user = cast(CurrentPrincipal, SimpleNamespace(id=4, firm_id=3))
    provider_error = AiProviderError(AiProviderErrorCode.RATE_LIMITED)
    service = cast(AIAssistanceService, SimpleNamespace(execute=AsyncMock(side_effect=provider_error)))
    payload = ExecuteAIAssistanceRequest(
        feature="intake_analysis",
        narrative="Relato suficientemente largo.",
        provider="gemini",
        model="gemini-3.5-flash-lite",
        confirmation_token="a" * 64,
    )
    request = cast(Request, SimpleNamespace(state=SimpleNamespace(request_id="req")))

    with pytest.raises(DomainError) as captured:
        await execute_assistance(2, payload, request, user, service)

    assert captured.value.error_type is DomainErrorType.RATE_LIMITED
    assert captured.value.detail == str(provider_error)
    assert captured.value.headers == {
        "Retry-After": str(AI_PROVIDER_RETRY_AFTER_SECONDS),
    }
    assert captured.value.layer is ErrorLayer.ROUTER


@run_async
@pytest.mark.parametrize(
    ("provider_code", "domain_error_type"),
    [
        (AiProviderErrorCode.AUTHENTICATION_FAILED, DomainErrorType.PROVIDER_AUTHENTICATION_FAILED),
        (AiProviderErrorCode.TIMEOUT, DomainErrorType.PROVIDER_TIMEOUT),
        (AiProviderErrorCode.UNAVAILABLE, DomainErrorType.PROVIDER_UNAVAILABLE),
        (AiProviderErrorCode.REQUEST_REJECTED, DomainErrorType.PROVIDER_REQUEST_REJECTED),
        (AiProviderErrorCode.INVALID_RESPONSE, DomainErrorType.PROVIDER_INVALID_RESPONSE),
        (AiProviderErrorCode.CONFIGURATION_ERROR, DomainErrorType.PROVIDER_CONFIGURATION_ERROR),
    ],
)
async def test_execute_maps_non_rate_limit_provider_errors(
    provider_code: AiProviderErrorCode,
    domain_error_type: DomainErrorType,
) -> None:
    user = cast(CurrentPrincipal, SimpleNamespace(id=4, firm_id=3))
    provider_error = AiProviderError(provider_code)
    service = cast(AIAssistanceService, SimpleNamespace(execute=AsyncMock(side_effect=provider_error)))
    payload = ExecuteAIAssistanceRequest(
        feature="intake_analysis",
        narrative="Relato suficientemente largo.",
        provider="gemini",
        model="gemini-3.5-flash-lite",
        confirmation_token="a" * 64,
    )
    request = cast(Request, SimpleNamespace(state=SimpleNamespace(request_id="req")))

    with pytest.raises(DomainError) as captured:
        await execute_assistance(2, payload, request, user, service)

    assert captured.value.error_type is domain_error_type
    assert captured.value.detail == str(provider_error)
    assert captured.value.headers is None
    assert captured.value.layer is ErrorLayer.ROUTER
