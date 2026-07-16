from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.matter_tasks.models import MatterTask
from app.features.matter_tasks.repository import MatterTasksRepository
from app.features.matter_tasks.schemas.api import CreateMatterTaskRequest, UpdateMatterTaskRequest


class MatterLookupPort(Protocol):
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class MatterTasksServicePort(Protocol):
    async def create(self, *, firm_id: int, matter_id: int, payload: CreateMatterTaskRequest) -> MatterTask: ...
    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterTask], int]: ...
    async def update(
        self, *, firm_id: int, matter_id: int, task_id: int, payload: UpdateMatterTaskRequest
    ) -> MatterTask: ...


class MatterTasksService:
    def __init__(
        self, repository: MatterTasksRepository, matters_repository: MatterLookupPort, unit_of_work: UnitOfWorkPort
    ):
        self.repository = repository
        self.matters_repository = matters_repository
        self.unit_of_work = unit_of_work

    async def _require_matter(self, *, firm_id: int, matter_id: int) -> None:
        if await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id) is None:
            raise NotFoundError("Matter not found")

    async def create(self, *, firm_id: int, matter_id: int, payload: CreateMatterTaskRequest) -> MatterTask:
        async with self.unit_of_work:
            await self._require_matter(firm_id=firm_id, matter_id=matter_id)
            return await self.repository.create(firm_id=firm_id, matter_id=matter_id, **payload.model_dump())

    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterTask], int]:
        await self._require_matter(firm_id=firm_id, matter_id=matter_id)
        return await self.repository.list_for_matter(
            matter_id=matter_id, firm_id=firm_id
        ), await self.repository.count_for_matter(matter_id=matter_id, firm_id=firm_id)

    async def update(
        self, *, firm_id: int, matter_id: int, task_id: int, payload: UpdateMatterTaskRequest
    ) -> MatterTask:
        async with self.unit_of_work:
            task = await self.repository.get_for_matter(task_id=task_id, matter_id=matter_id, firm_id=firm_id)
            if task is None:
                raise NotFoundError("Matter task not found")
            return await self.repository.update(task, **payload.model_dump(exclude_unset=True))
