import asyncio
from functools import wraps
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import Request

from app.core.config.settings import AILimitSettings
from app.core.errors.domain import DomainError, DomainErrorType
from app.core.errors.services import ConflictError, InvalidInputError
from app.features.auth.principal import CurrentPrincipal
from app.features.document_templates.catalog import DocumentTemplateKey
from app.features.document_templates.router import (
    AI_PROVIDER_RETRY_AFTER_SECONDS,
    _firm_id,
    generate_document_draft,
    preview_document_draft,
)
from app.features.document_templates.schemas.api import (
    DocumentDraftPreviewRequest,
    GenerateDocumentDraftRequest,
)
from app.features.document_templates.service import DocumentTemplatesService
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode, AiTextResponse


def run_async(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))

    return wrapper


def payload(**changes):
    values = {
        "template_key": "document_request",
        "fields": {
            "recipient_name": "Ana",
            "matter_reference": "Expediente 1",
            "requested_documents": "Identificación y comprobante",
            "delivery_deadline": "2026-08-15",
            "delivery_method": "",
        },
        "provider": "openai",
        "model": "gpt-4.1-mini",
    }
    values.update(changes)
    return DocumentDraftPreviewRequest(**values)


def service(*, provider_error=None, limits=None):
    provider = SimpleNamespace(
        generate=AsyncMock(
            side_effect=provider_error,
            return_value=AiTextResponse(provider="openai", model="gpt-4.1-mini", text='{"content":"Borrador"}'),
        )
    )
    factory = SimpleNamespace(build=AsyncMock(return_value=provider))
    job = SimpleNamespace(execution_id="execution-1")
    jobs = SimpleNamespace(
        create=AsyncMock(return_value=job),
        start=AsyncMock(),
        succeed=AsyncMock(),
        fail=AsyncMock(),
    )
    return (
        DocumentTemplatesService(
            provider_factory=factory,
            jobs_service=jobs,
            preview_signing_key="secret",
            limits=limits,
        ),
        provider,
        jobs,
    )


@run_async
async def test_preview_and_generate_schema_validated_editable_draft() -> None:
    draft_service, provider, jobs = service()
    request = payload()
    preview = draft_service.preview(firm_id=3, payload=request)

    assert preview.included_fields == [
        "Nombre de la persona destinataria",
        "Referencia del asunto",
        "Documentos solicitados",
        "Fecha límite de entrega",
    ]
    assert preview.character_count > 0
    result = await draft_service.generate(
        firm_id=3,
        user_id=4,
        request_id="req-1",
        payload=request,
        confirmation_token=preview.confirmation_token,
    )
    assert result.content == "Borrador"
    assert result.status == "draft"
    assert result.requires_professional_review is True
    provider.generate.assert_awaited_once()
    jobs.succeed.assert_awaited_once()


def test_preview_enforces_configured_draft_limits() -> None:
    limits = AILimitSettings(DOCUMENT_DRAFT_FIELD_MAX_CHARS=10, DOCUMENT_DRAFT_OUTPUT_MAX_TOKENS=456)
    draft_service, _, _ = service(limits=limits)
    with pytest.raises(InvalidInputError, match="allowed size"):
        draft_service.preview(firm_id=3, payload=payload())

    request = payload(
        fields={
            "recipient_name": "Ana",
            "matter_reference": "Uno",
            "requested_documents": "Dos",
            "delivery_deadline": "2026-08-15",
        }
    )
    preview = draft_service.preview(firm_id=3, payload=request)
    assert preview.estimated_max_output_tokens == 456


@run_async
async def test_generate_rejects_stale_preview_and_records_provider_failure() -> None:
    provider_error = AiProviderError(AiProviderErrorCode.TIMEOUT)
    draft_service, _, jobs = service(provider_error=provider_error)
    request = payload()
    with pytest.raises(ConflictError):
        await draft_service.generate(
            firm_id=3,
            user_id=4,
            request_id="req",
            payload=request,
            confirmation_token="0" * 64,
        )
    preview = draft_service.preview(firm_id=3, payload=request)
    with pytest.raises(AiProviderError):
        await draft_service.generate(
            firm_id=3,
            user_id=4,
            request_id="req",
            payload=request,
            confirmation_token=preview.confirmation_token,
        )
    jobs.fail.assert_awaited_once()


@pytest.mark.parametrize(
    "fields",
    [
        {"recipient_name": "Ana"},
        {
            "recipient_name": "Ana",
            "matter_reference": "Asunto",
            "requested_documents": "INE",
            "delivery_deadline": "2026-08-15",
            "unknown": "value",
        },
        {
            "recipient_name": "x" * 20001,
            "matter_reference": "Asunto",
            "requested_documents": "INE",
            "delivery_deadline": "2026-08-15",
        },
    ],
)
def test_preview_rejects_invalid_template_fields(fields: dict[str, str]) -> None:
    draft_service, _, _ = service()
    with pytest.raises(InvalidInputError):
        draft_service.preview(firm_id=3, payload=payload(fields=fields))


def test_preview_rejects_unknown_template_defensively() -> None:
    draft_service, _, _ = service()
    invalid = DocumentDraftPreviewRequest.model_construct(
        template_key=cast(DocumentTemplateKey, "unknown"),
        fields={"name": "value"},
        provider="openai",
        model="model",
    )
    with pytest.raises(InvalidInputError):
        draft_service.preview(firm_id=3, payload=invalid)


@run_async
async def test_router_delegates_identity_and_maps_provider_errors() -> None:
    user = cast(CurrentPrincipal, SimpleNamespace(id=4, firm_id=3))
    preview_payload = payload()
    generated_payload = GenerateDocumentDraftRequest(**preview_payload.model_dump(), confirmation_token="a" * 64)
    draft_service = cast(
        DocumentTemplatesService,
        SimpleNamespace(preview=lambda **kwargs: "preview", generate=AsyncMock(return_value="draft")),
    )
    assert await preview_document_draft(preview_payload, user, draft_service) == "preview"
    request = cast(Request, SimpleNamespace(state=SimpleNamespace(request_id="req")))
    assert await generate_document_draft(generated_payload, request, user, draft_service) == "draft"
    assert _firm_id(user) == 3
    with pytest.raises(ValueError):
        _firm_id(cast(CurrentPrincipal, SimpleNamespace(firm_id=None)))

    for code in AiProviderErrorCode:
        failing = cast(
            DocumentTemplatesService,
            SimpleNamespace(generate=AsyncMock(side_effect=AiProviderError(code))),
        )
        with pytest.raises(DomainError) as captured:
            await generate_document_draft(generated_payload, request, user, failing)
        if code is AiProviderErrorCode.RATE_LIMITED:
            assert captured.value.error_type is DomainErrorType.RATE_LIMITED
            assert captured.value.headers == {"Retry-After": str(AI_PROVIDER_RETRY_AFTER_SECONDS)}
