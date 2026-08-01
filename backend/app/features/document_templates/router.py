from fastapi import APIRouter, Request, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.errors.domain import DomainError, DomainErrorType, ErrorLayer
from app.core.setup.dependencies import DocumentTemplatesServiceDependency
from app.features.document_templates.catalog import DOCUMENT_TEMPLATES
from app.features.document_templates.openapi import (
    GENERATE_DOCUMENT_DRAFT_DOC,
    LIST_DOCUMENT_TEMPLATES_DOC,
    PREVIEW_DOCUMENT_DRAFT_DOC,
)
from app.features.document_templates.schemas.api import (
    DocumentDraftPreviewRequest,
    DocumentDraftPreviewResponse,
    DocumentDraftResponse,
    DocumentTemplateFieldResponse,
    DocumentTemplateListResponse,
    DocumentTemplateResponse,
    GenerateDocumentDraftRequest,
)
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode

router = APIRouter(prefix="/document-templates", tags=["document-templates"])
AI_PROVIDER_RETRY_AFTER_SECONDS = 60
AI_PROVIDER_ERROR_TYPES = {
    AiProviderErrorCode.AUTHENTICATION_FAILED: DomainErrorType.PROVIDER_AUTHENTICATION_FAILED,
    AiProviderErrorCode.TIMEOUT: DomainErrorType.PROVIDER_TIMEOUT,
    AiProviderErrorCode.UNAVAILABLE: DomainErrorType.PROVIDER_UNAVAILABLE,
    AiProviderErrorCode.REQUEST_REJECTED: DomainErrorType.PROVIDER_REQUEST_REJECTED,
    AiProviderErrorCode.INVALID_RESPONSE: DomainErrorType.PROVIDER_INVALID_RESPONSE,
    AiProviderErrorCode.CONFIGURATION_ERROR: DomainErrorType.PROVIDER_CONFIGURATION_ERROR,
}


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated document template users must belong to a firm")
    return user.firm_id


def _raise_provider_http_error(error: AiProviderError) -> None:
    if error.code is AiProviderErrorCode.RATE_LIMITED:
        raise DomainError(
            DomainErrorType.RATE_LIMITED,
            str(error),
            headers={"Retry-After": str(AI_PROVIDER_RETRY_AFTER_SECONDS)},
            layer=ErrorLayer.ROUTER,
        ) from error
    raise DomainError(AI_PROVIDER_ERROR_TYPES[error.code], str(error), layer=ErrorLayer.ROUTER) from error


@router.get("", response_model=DocumentTemplateListResponse, **LIST_DOCUMENT_TEMPLATES_DOC)
async def list_document_templates(user: AuthenticatedReadAccessDependency):
    del user
    return DocumentTemplateListResponse(
        items=[
            DocumentTemplateResponse(
                key=template.key,
                name=template.name,
                description=template.description,
                purpose=template.purpose,
                fields=[
                    DocumentTemplateFieldResponse(
                        key=field.key,
                        label=field.label,
                        field_type=field.field_type,
                        required=field.required,
                    )
                    for field in template.fields
                ],
            )
            for template in DOCUMENT_TEMPLATES
        ]
    )


@router.post("/drafts/preview", response_model=DocumentDraftPreviewResponse, **PREVIEW_DOCUMENT_DRAFT_DOC)
async def preview_document_draft(
    payload: DocumentDraftPreviewRequest,
    user: AuthenticatedReadAccessDependency,
    service: DocumentTemplatesServiceDependency,
):
    return service.preview(firm_id=_firm_id(user), payload=payload)


@router.post(
    "/drafts",
    response_model=DocumentDraftResponse,
    status_code=status.HTTP_201_CREATED,
    **GENERATE_DOCUMENT_DRAFT_DOC,
)
async def generate_document_draft(
    payload: GenerateDocumentDraftRequest,
    request: Request,
    user: AuthenticatedReadAccessDependency,
    service: DocumentTemplatesServiceDependency,
):
    try:
        return await service.generate(
            firm_id=_firm_id(user),
            user_id=user.id,
            request_id=getattr(request.state, "request_id", "-"),
            payload=payload,
            confirmation_token=payload.confirmation_token,
        )
    except AiProviderError as error:
        _raise_provider_http_error(error)
