from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.matter_checklists.models import MatterChecklistItem
from app.features.matter_checklists.repository import MatterChecklistsRepository
from app.features.matter_checklists.schemas.api import CreateChecklistItemRequest, UpdateChecklistItemRequest
from app.features.matter_checklists.templates import checklist_for


class MatterLookupPort(Protocol):
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class MatterChecklistsServicePort(Protocol):
    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterChecklistItem], int]: ...
    async def create(
        self, *, firm_id: int, matter_id: int, payload: CreateChecklistItemRequest
    ) -> MatterChecklistItem: ...
    async def update(
        self, *, firm_id: int, matter_id: int, item_id: int, payload: UpdateChecklistItemRequest
    ) -> MatterChecklistItem: ...


class MatterChecklistsService:
    def __init__(
        self, repository: MatterChecklistsRepository, matters_repository: MatterLookupPort, unit_of_work: UnitOfWorkPort
    ):
        self.repository = repository
        self.matters_repository = matters_repository
        self.unit_of_work = unit_of_work

    async def _require_matter(self, *, firm_id: int, matter_id: int):
        matter = await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id)
        if matter is None:
            raise NotFoundError("Matter not found")
        return matter

    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterChecklistItem], int]:
        async with self.unit_of_work:
            matter = await self._require_matter(firm_id=firm_id, matter_id=matter_id)
            if await self.repository.count_for_matter(matter_id=matter_id, firm_id=firm_id) == 0:
                for position, label in enumerate(checklist_for(matter.matter_type)):
                    await self.repository.create(
                        firm_id=firm_id,
                        matter_id=matter_id,
                        label=label,
                        template_key=str(position),
                        position=position,
                        is_custom=False,
                    )
            items = await self.repository.list_for_matter(matter_id=matter_id, firm_id=firm_id)
            return items, len(items)

    async def create(self, *, firm_id: int, matter_id: int, payload: CreateChecklistItemRequest) -> MatterChecklistItem:
        async with self.unit_of_work:
            await self._require_matter(firm_id=firm_id, matter_id=matter_id)
            position = await self.repository.count_for_matter(matter_id=matter_id, firm_id=firm_id)
            return await self.repository.create(
                firm_id=firm_id, matter_id=matter_id, label=payload.label, position=position, is_custom=True
            )

    async def update(
        self, *, firm_id: int, matter_id: int, item_id: int, payload: UpdateChecklistItemRequest
    ) -> MatterChecklistItem:
        async with self.unit_of_work:
            item = await self.repository.get_for_matter(item_id=item_id, matter_id=matter_id, firm_id=firm_id)
            if item is None:
                raise NotFoundError("Checklist item not found")
            return await self.repository.update(item, status=payload.status)
