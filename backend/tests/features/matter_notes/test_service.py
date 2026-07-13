import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors.services import NotFoundError
from app.features.auth.principal import CurrentPrincipal
from app.features.matter_notes.router import _firm_id
from app.features.matter_notes.schemas.api import CreateMatterNoteRequest, UpdateMatterNoteRequest
from app.features.matter_notes.service import MatterNotesService


def test_service_requires_firm_scoped_matter() -> None:
    async def run() -> None:
        notes, matters = AsyncMock(), AsyncMock()
        uow = MagicMock()
        uow.__aenter__ = AsyncMock()
        uow.__aexit__ = AsyncMock(return_value=False)
        service = MatterNotesService(notes, matters, uow)
        matters.get_for_firm.return_value = None
        with pytest.raises(NotFoundError):
            await service.create(firm_id=1, matter_id=2, payload=CreateMatterNoteRequest(content="Nota"))

    asyncio.run(run())


def test_note_schemas_normalize_and_reject_invalid_updates() -> None:
    assert CreateMatterNoteRequest(content="  Nota  ").content == "Nota"
    assert UpdateMatterNoteRequest(content="  Cambio  ").content == "Cambio"
    assert UpdateMatterNoteRequest(is_relevant=False).is_relevant is False
    with pytest.raises(ValidationError):
        UpdateMatterNoteRequest(content="  ")
    with pytest.raises(ValidationError):
        UpdateMatterNoteRequest(content=None)
    with pytest.raises(ValidationError):
        UpdateMatterNoteRequest()


def test_note_router_requires_a_firm() -> None:
    principal = CurrentPrincipal(
        id=1,
        email="none@example.com",
        first_name="N",
        last_name="O",
        display_name="N O",
        disabled=False,
        firm_id=None,
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)
