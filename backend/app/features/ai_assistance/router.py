from fastapi import APIRouter, Request, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.errors.domain import DomainError, DomainErrorType, ErrorLayer
from app.core.setup.dependencies import AIAssistanceServiceDependency
from app.features.ai_assistance.openapi import CONVERT_DOC, EXECUTE_DOC, LIST_DOC, PREVIEW_DOC, REVIEW_DOC
from app.features.ai_assistance.schemas import (
    AIAssistanceResultListResponse,
    AIAssistanceResultResponse,
    AIContextPreviewRequest,
    AIContextPreviewResponse,
    ConvertAIAssistanceRequest,
    ExecuteAIAssistanceRequest,
    ReviewAIAssistanceRequest,
)
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode

router = APIRouter(prefix="/matters/{matter_id}/ai", tags=["ai-assistance"])
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
        raise ValueError("Authenticated AI users must belong to a firm")
    return user.firm_id


def _raise_provider_http_error(error: AiProviderError) -> None:
    if error.code is AiProviderErrorCode.RATE_LIMITED:
        raise DomainError(
            DomainErrorType.RATE_LIMITED,
            str(error),
            headers={"Retry-After": str(AI_PROVIDER_RETRY_AFTER_SECONDS)},
            layer=ErrorLayer.ROUTER,
        ) from error
    raise DomainError(
        AI_PROVIDER_ERROR_TYPES[error.code],
        str(error),
        layer=ErrorLayer.ROUTER,
    ) from error


@router.post("/preview", response_model=AIContextPreviewResponse, **PREVIEW_DOC)
async def preview_context(
    matter_id: int,
    payload: AIContextPreviewRequest,
    user: AuthenticatedReadAccessDependency,
    service: AIAssistanceServiceDependency,
):
    return await service.preview(matter_id=matter_id, firm_id=_firm_id(user), payload=payload)


@router.post("/results", response_model=AIAssistanceResultResponse, status_code=status.HTTP_201_CREATED, **EXECUTE_DOC)
async def execute_assistance(
    matter_id: int,
    payload: ExecuteAIAssistanceRequest,
    request: Request,
    user: AuthenticatedReadAccessDependency,
    service: AIAssistanceServiceDependency,
):
    request_id = getattr(request.state, "request_id", "-")
    try:
        return await service.execute(
            matter_id=matter_id,
            firm_id=_firm_id(user),
            user_id=user.id,
            request_id=request_id,
            payload=payload,
        )
    except AiProviderError as error:
        _raise_provider_http_error(error)


@router.get("/results", response_model=AIAssistanceResultListResponse, **LIST_DOC)
async def list_results(matter_id: int, user: AuthenticatedReadAccessDependency, service: AIAssistanceServiceDependency):
    items, total = await service.list(matter_id=matter_id, firm_id=_firm_id(user))
    return AIAssistanceResultListResponse(items=items, total=total)


@router.patch("/results/{result_id}", response_model=AIAssistanceResultResponse, **REVIEW_DOC)
async def review_result(
    matter_id: int,
    result_id: int,
    payload: ReviewAIAssistanceRequest,
    user: AuthenticatedReadAccessDependency,
    service: AIAssistanceServiceDependency,
):
    return await service.review(result_id=result_id, matter_id=matter_id, firm_id=_firm_id(user), payload=payload)


@router.post("/results/{result_id}/actions", response_model=AIAssistanceResultResponse, **CONVERT_DOC)
async def convert_result(
    matter_id: int,
    result_id: int,
    payload: ConvertAIAssistanceRequest,
    user: AuthenticatedReadAccessDependency,
    service: AIAssistanceServiceDependency,
):
    return await service.convert(result_id=result_id, matter_id=matter_id, firm_id=_firm_id(user), payload=payload)
