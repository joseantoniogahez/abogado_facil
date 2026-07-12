from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.clients.models import Client
from app.features.clients.repository import ClientsRepository
from app.features.clients.schemas.api import CreateClientRequest, UpdateClientRequest


class ClientsServicePort(Protocol):
    async def create(self, *, firm_id: int, payload: CreateClientRequest) -> Client: ...
    async def list(self, *, firm_id: int, search: str | None, limit: int, offset: int) -> tuple[list[Client], int]: ...
    async def get(self, *, firm_id: int, client_id: int) -> Client: ...
    async def update(self, *, firm_id: int, client_id: int, payload: UpdateClientRequest) -> Client: ...


class ClientsService:
    def __init__(self, *, repository: ClientsRepository, unit_of_work: UnitOfWorkPort):
        self.repository = repository
        self.unit_of_work = unit_of_work

    async def create(self, *, firm_id: int, payload: CreateClientRequest) -> Client:
        async with self.unit_of_work:
            return await self.repository.create(firm_id=firm_id, **payload.model_dump())

    async def list(self, *, firm_id: int, search: str | None, limit: int, offset: int) -> tuple[list[Client], int]:
        return (
            await self.repository.list_for_firm(firm_id=firm_id, search=search, limit=limit, offset=offset),
            await self.repository.count_for_firm(firm_id=firm_id, search=search),
        )

    async def get(self, *, firm_id: int, client_id: int) -> Client:
        client = await self.repository.get_for_firm(client_id=client_id, firm_id=firm_id)
        if client is None:
            raise NotFoundError("Client not found")
        return client

    async def update(self, *, firm_id: int, client_id: int, payload: UpdateClientRequest) -> Client:
        async with self.unit_of_work:
            client = await self.get(firm_id=firm_id, client_id=client_id)
            return await self.repository.update(client, **payload.model_dump(exclude_unset=True))
