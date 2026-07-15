import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors.services import NotFoundError
from app.features.auth.principal import CurrentPrincipal
from app.features.matter_checklists.router import _firm_id
from app.features.matter_checklists.schemas.api import CreateChecklistItemRequest, UpdateChecklistItemRequest
from app.features.matter_checklists.service import MatterChecklistsService
from app.features.matter_checklists.templates import checklist_for, normalize_matter_type


def test_templates_normalize_accents_and_supported_types() -> None:
    assert normalize_matter_type("  Pensión / alimenticia ") == "pension alimenticia"
    assert checklist_for("Pensión alimenticia")
    assert checklist_for("Tipo libre") == ()


def test_checklist_schemas_normalize_and_validate() -> None:
    assert CreateChecklistItemRequest(label="  Documento  ").label == "Documento"
    assert UpdateChecklistItemRequest(status="not_applicable").status == "not_applicable"
    with pytest.raises(ValidationError):
        CreateChecklistItemRequest(label=" ")
    with pytest.raises(ValidationError):
        UpdateChecklistItemRequest(status="invalid")


def test_checklist_update_hides_unknown_item_and_router_requires_firm() -> None:
    async def run() -> None:
        repository, matters = AsyncMock(), AsyncMock()
        uow = MagicMock()
        uow.__aenter__ = AsyncMock()
        uow.__aexit__ = AsyncMock(return_value=False)
        repository.get_for_matter.return_value = None
        service = MatterChecklistsService(repository, matters, uow)
        with pytest.raises(NotFoundError):
            await service.update(
                firm_id=1, matter_id=2, item_id=3, payload=UpdateChecklistItemRequest(status="pending")
            )

    asyncio.run(run())
    principal = CurrentPrincipal(
        id=1, email="none@example.com", first_name="N", last_name="O", display_name="N O", disabled=False, firm_id=None
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)
