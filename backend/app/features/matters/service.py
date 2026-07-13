from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.matters.models import Matter
from app.features.matters.repository import MattersRepository
from app.features.matters.schemas.api import CreateMatterRequest, UpdateMatterRequest


class MattersServicePort(Protocol):
    async def create(self, *, firm_id: int, payload: CreateMatterRequest) -> Matter: ...
    async def list(
        self, *, firm_id: int, client_id: int | None, limit: int, offset: int
    ) -> tuple[list[Matter], int]: ...
    async def get(self, *, firm_id: int, matter_id: int) -> Matter: ...
    async def update(self, *, firm_id: int, matter_id: int, payload: UpdateMatterRequest) -> Matter: ...


class ClientLookupPort(Protocol):
    async def get_for_firm(self, *, client_id: int, firm_id: int): ...


class MattersService:
    def __init__(
        self, repository: MattersRepository, clients_repository: ClientLookupPort, unit_of_work: UnitOfWorkPort
    ):
        self.repository, self.clients_repository, self.unit_of_work = repository, clients_repository, unit_of_work

    async def create(self, *, firm_id: int, payload: CreateMatterRequest) -> Matter:
        async with self.unit_of_work:
            if await self.clients_repository.get_for_firm(client_id=payload.client_id, firm_id=firm_id) is None:
                raise NotFoundError("Client not found")
            return await self.repository.create(firm_id=firm_id, **payload.model_dump())

    async def list(self, *, firm_id: int, client_id: int | None, limit: int, offset: int) -> tuple[list[Matter], int]:
        if (
            client_id is not None
            and await self.clients_repository.get_for_firm(client_id=client_id, firm_id=firm_id) is None
        ):
            raise NotFoundError("Client not found")
        return await self.repository.list_for_firm(
            firm_id=firm_id, client_id=client_id, limit=limit, offset=offset
        ), await self.repository.count_for_firm(firm_id=firm_id, client_id=client_id)

    async def get(self, *, firm_id: int, matter_id: int) -> Matter:
        matter = await self.repository.get_for_firm(matter_id=matter_id, firm_id=firm_id)
        if matter is None:
            raise NotFoundError("Matter not found")
        return matter

    async def update(self, *, firm_id: int, matter_id: int, payload: UpdateMatterRequest) -> Matter:
        async with self.unit_of_work:
            matter = await self.get(firm_id=firm_id, matter_id=matter_id)
            return await self.repository.update(matter, **payload.model_dump(exclude_unset=True))
