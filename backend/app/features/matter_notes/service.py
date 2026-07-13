from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.matter_notes.models import MatterNote
from app.features.matter_notes.repository import MatterNotesRepository
from app.features.matter_notes.schemas.api import CreateMatterNoteRequest, UpdateMatterNoteRequest


class MatterLookupPort(Protocol):
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class MatterNotesServicePort(Protocol):
    async def create(self, *, firm_id: int, matter_id: int, payload: CreateMatterNoteRequest) -> MatterNote: ...
    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterNote], int]: ...
    async def update(
        self, *, firm_id: int, matter_id: int, note_id: int, payload: UpdateMatterNoteRequest
    ) -> MatterNote: ...
    async def delete(self, *, firm_id: int, matter_id: int, note_id: int) -> None: ...


class MatterNotesService:
    def __init__(
        self, repository: MatterNotesRepository, matters_repository: MatterLookupPort, unit_of_work: UnitOfWorkPort
    ):
        self.repository = repository
        self.matters_repository = matters_repository
        self.unit_of_work = unit_of_work

    async def _require_matter(self, *, firm_id: int, matter_id: int) -> None:
        if await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id) is None:
            raise NotFoundError("Matter not found")

    async def _require_note(self, *, firm_id: int, matter_id: int, note_id: int) -> MatterNote:
        note = await self.repository.get_for_matter(note_id=note_id, matter_id=matter_id, firm_id=firm_id)
        if note is None:
            raise NotFoundError("Matter note not found")
        return note

    async def create(self, *, firm_id: int, matter_id: int, payload: CreateMatterNoteRequest) -> MatterNote:
        async with self.unit_of_work:
            await self._require_matter(firm_id=firm_id, matter_id=matter_id)
            return await self.repository.create(firm_id=firm_id, matter_id=matter_id, **payload.model_dump())

    async def list(self, *, firm_id: int, matter_id: int) -> tuple[list[MatterNote], int]:
        await self._require_matter(firm_id=firm_id, matter_id=matter_id)
        return await self.repository.list_for_matter(
            matter_id=matter_id, firm_id=firm_id
        ), await self.repository.count_for_matter(matter_id=matter_id, firm_id=firm_id)

    async def update(
        self, *, firm_id: int, matter_id: int, note_id: int, payload: UpdateMatterNoteRequest
    ) -> MatterNote:
        async with self.unit_of_work:
            note = await self._require_note(firm_id=firm_id, matter_id=matter_id, note_id=note_id)
            return await self.repository.update(note, **payload.model_dump(exclude_unset=True))

    async def delete(self, *, firm_id: int, matter_id: int, note_id: int) -> None:
        async with self.unit_of_work:
            note = await self._require_note(firm_id=firm_id, matter_id=matter_id, note_id=note_id)
            await self.repository.delete(note.id)
