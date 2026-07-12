import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors.services import NotFoundError
from app.features.auth.principal import CurrentPrincipal
from app.features.clients.router import _firm_id
from app.features.clients.schemas.api import CreateClientRequest, UpdateClientRequest
from app.features.clients.service import ClientsService


def _service() -> tuple[ClientsService, AsyncMock, MagicMock]:
    repository = AsyncMock()
    unit_of_work = MagicMock()
    unit_of_work.__aenter__ = AsyncMock()
    unit_of_work.__aexit__ = AsyncMock(return_value=False)
    return ClientsService(repository=repository, unit_of_work=unit_of_work), repository, unit_of_work


def test_create_and_update_use_unit_of_work() -> None:
    async def run() -> None:
        service, repository, uow = _service()
        repository.create.return_value = object()
        await service.create(firm_id=4, payload=CreateClientRequest(full_name="Ana", phone="55 1234 5678"))
        repository.create.assert_awaited_once_with(
            firm_id=4, full_name="Ana", phone="5512345678", email=None, address=None, notes=None
        )
        assert uow.__aenter__.await_count == 1

        entity = object()
        repository.get_for_firm.return_value = entity
        repository.update.return_value = entity
        await service.update(firm_id=4, client_id=9, payload=UpdateClientRequest(notes="Nota"))
        repository.update.assert_awaited_once_with(entity, notes="Nota")
        assert uow.__aenter__.await_count == 2

    asyncio.run(run())


def test_client_schema_normalization_and_rejections() -> None:
    payload = CreateClientRequest(full_name=" Ana ", phone="+52 (55) 1234-5678", address=" ", notes=None)
    assert payload.full_name == "Ana"
    assert payload.phone == "5512345678"
    assert payload.address is None
    with pytest.raises(ValidationError):
        CreateClientRequest(full_name=" ", phone="5512345678")
    assert UpdateClientRequest(full_name=None).full_name is None
    assert UpdateClientRequest(full_name=" Ana ").full_name == "Ana"
    with pytest.raises(ValidationError):
        UpdateClientRequest(full_name=" ")
    with pytest.raises(ValidationError):
        UpdateClientRequest(phone="123")
    with pytest.raises(ValidationError):
        UpdateClientRequest()


def test_client_routes_reject_principal_without_firm() -> None:
    principal = CurrentPrincipal(
        id=1,
        email="orphan@example.com",
        first_name="O",
        last_name="U",
        display_name="O U",
        disabled=False,
        firm_id=None,
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)


def test_get_hides_missing_or_foreign_client() -> None:
    async def run() -> None:
        service, repository, _ = _service()
        repository.get_for_firm.return_value = None
        try:
            await service.get(firm_id=3, client_id=99)
        except NotFoundError as error:
            assert error.message == "Client not found"
        else:
            raise AssertionError("Expected NotFoundError")

    asyncio.run(run())
