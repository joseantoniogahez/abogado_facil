import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.features.ai_credentials.router import delete_credential, list_credentials, list_models, save_credential
from app.features.ai_credentials.schemas import (
    AiCredentialListResponse,
    AiCredentialResponse,
    AiModelCatalogResponse,
    SaveAiCredentialRequest,
)
from app.features.auth.principal import CurrentPrincipal


def _principal(*, firm_id: int | None) -> CurrentPrincipal:
    return CurrentPrincipal(
        id=7,
        email="user@example.com",
        first_name="Test",
        last_name="User",
        display_name="Test User",
        disabled=False,
        firm_id=firm_id,
    )


def test_router_delegates_and_uses_authenticated_firm() -> None:
    async def run() -> None:
        user = _principal(firm_id=9)
        service = AsyncMock()
        service.list.return_value = AiCredentialListResponse(items=[])
        service.list_models.return_value = AiModelCatalogResponse(providers=[])
        now = datetime.now(UTC)
        service.save.return_value = AiCredentialResponse(
            provider="openai", configured=True, created_at=now, updated_at=now
        )
        assert await list_credentials(user, service) == AiCredentialListResponse(items=[])
        assert await list_models(user, service) == AiModelCatalogResponse(providers=[])
        assert await save_credential(  # pragma: allowlist secret
            "openai",
            SaveAiCredentialRequest(api_key="secret-value"),  # pragma: allowlist secret
            user,
            service,  # pragma: allowlist secret
        )
        await delete_credential("openai", user, service)
        service.list.assert_awaited_once_with(user_id=7, firm_id=9)
        service.list_models.assert_awaited_once_with(user_id=7, firm_id=9)
        service.save.assert_awaited_once_with(user_id=7, firm_id=9, provider="openai", api_key="secret-value")
        service.delete.assert_awaited_once_with(user_id=7, firm_id=9, provider="openai")

    asyncio.run(run())


def test_router_rejects_user_without_firm() -> None:
    with pytest.raises(ValueError, match="firm"):
        asyncio.run(list_credentials(_principal(firm_id=None), AsyncMock()))
