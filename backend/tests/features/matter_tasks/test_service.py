import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors.services import NotFoundError
from app.features.auth.principal import CurrentPrincipal
from app.features.matter_tasks.router import _firm_id
from app.features.matter_tasks.schemas.api import CreateMatterTaskRequest, UpdateMatterTaskRequest
from app.features.matter_tasks.service import MatterTasksService


def test_task_schemas_normalize_and_validate() -> None:
    assert CreateMatterTaskRequest(title="  Audiencia  ", due_date=date(2026, 7, 20)).title == "Audiencia"
    assert UpdateMatterTaskRequest(completed=True).completed is True
    assert UpdateMatterTaskRequest(title="  Escrito  ").title == "Escrito"
    assert UpdateMatterTaskRequest(due_date=date(2026, 7, 21)).due_date == date(2026, 7, 21)
    with pytest.raises(ValidationError):
        UpdateMatterTaskRequest()
    with pytest.raises(ValidationError):
        UpdateMatterTaskRequest(title=None)
    with pytest.raises(ValidationError):
        UpdateMatterTaskRequest(title=" ")
    with pytest.raises(ValidationError):
        UpdateMatterTaskRequest(due_date=None)


def test_task_service_hides_unknown_resources_and_requires_firm() -> None:
    async def run() -> None:
        repository, matters = AsyncMock(), AsyncMock()
        uow = MagicMock()
        uow.__aenter__ = AsyncMock()
        uow.__aexit__ = AsyncMock(return_value=False)
        matters.get_for_firm.return_value = None
        service = MatterTasksService(repository, matters, uow)
        with pytest.raises(NotFoundError):
            await service.create(
                firm_id=1,
                matter_id=2,
                payload=CreateMatterTaskRequest(title="Audiencia", due_date=date(2026, 7, 20)),
            )
        repository.get_for_matter.return_value = None
        with pytest.raises(NotFoundError):
            await service.update(firm_id=1, matter_id=2, task_id=3, payload=UpdateMatterTaskRequest(completed=True))

    asyncio.run(run())
    principal = CurrentPrincipal(
        id=1, email="none@example.com", first_name="N", last_name="O", display_name="N O", disabled=False, firm_id=None
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)
