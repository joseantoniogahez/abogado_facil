from fastapi import APIRouter, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import AiCredentialsServiceDependency
from app.features.ai_credentials.schemas import AiCredentialListResponse, AiCredentialResponse, SaveAiCredentialRequest

router = APIRouter(prefix="/ai/credentials", tags=["ai-credentials"])


def _firm_id(user) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated user must belong to a firm")
    return user.firm_id


@router.get("", response_model=AiCredentialListResponse)
async def list_credentials(
    user: AuthenticatedReadAccessDependency, service: AiCredentialsServiceDependency
) -> AiCredentialListResponse:
    return await service.list(user_id=user.id, firm_id=_firm_id(user))


@router.put("/{provider}", response_model=AiCredentialResponse, status_code=status.HTTP_200_OK)
async def save_credential(
    provider: str,
    payload: SaveAiCredentialRequest,
    user: AuthenticatedReadAccessDependency,
    service: AiCredentialsServiceDependency,
) -> AiCredentialResponse:
    return await service.save(user_id=user.id, firm_id=_firm_id(user), provider=provider, api_key=payload.api_key)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    provider: str, user: AuthenticatedReadAccessDependency, service: AiCredentialsServiceDependency
) -> None:
    await service.delete(user_id=user.id, firm_id=_firm_id(user), provider=provider)
