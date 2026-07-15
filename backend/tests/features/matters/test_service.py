import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors.services import NotFoundError
from app.features.auth.principal import CurrentPrincipal
from app.features.matters.router import _firm_id
from app.features.matters.schemas.api import CreateMatterRequest, MatterResponse, UpdateMatterRequest
from app.features.matters.service import MattersService


def _service():
    repository, clients = AsyncMock(), AsyncMock()
    uow = MagicMock()
    uow.__aenter__ = AsyncMock()
    uow.__aexit__ = AsyncMock(return_value=False)
    return MattersService(repository, clients, uow), repository, clients


def test_service_validates_client_and_updates() -> None:
    async def run() -> None:
        service, repository, clients = _service()
        clients.get_for_firm.return_value = object()
        repository.create.return_value = object()
        await service.create(firm_id=1, payload=CreateMatterRequest(client_id=2, title=" Civil ", matter_type="Otro"))
        repository.create.assert_awaited_once()
        repository.get_for_firm.return_value = None
        with pytest.raises(NotFoundError):
            await service.get(firm_id=1, matter_id=9)
        clients.get_for_firm.return_value = None
        with pytest.raises(NotFoundError):
            await service.list(firm_id=1, client_id=8, limit=10, offset=0)

    asyncio.run(run())


def test_matter_schema_rejects_invalid_changes() -> None:
    with pytest.raises(ValidationError):
        CreateMatterRequest(client_id=1, title=" ", matter_type="Otro")
    with pytest.raises(ValidationError):
        CreateMatterRequest(client_id=1, title="Civil", matter_type="Civil")
    legacy = MatterResponse(
        id=1,
        client_id=1,
        title="Legado",
        matter_type="Civil histórico",
        status="active",
        counterparty=None,
        description=None,
        next_action=None,
        next_action_date=None,
        created_at="2026-07-15T00:00:00Z",
        updated_at="2026-07-15T00:00:00Z",
    )
    assert legacy.matter_type == "Civil histórico"
    with pytest.raises(ValidationError):
        UpdateMatterRequest()
    principal = CurrentPrincipal(
        id=1, email="none@example.com", first_name="N", last_name="O", display_name="N O", disabled=False, firm_id=None
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)
