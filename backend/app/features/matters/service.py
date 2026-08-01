from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import InternalError, NotFoundError
from app.features.matters.models import Matter
from app.features.matters.repository import MattersRepository
from app.features.matters.schemas.api import CreateMatterRequest, UpdateMatterRequest
from app.integrations.files import FileStorageError, FileStoragePort


class MattersServicePort(Protocol):
    async def create(self, *, firm_id: int, payload: CreateMatterRequest) -> Matter: ...
    async def list(
        self, *, firm_id: int, client_id: int | None, limit: int, offset: int
    ) -> tuple[list[Matter], int]: ...
    async def get(self, *, firm_id: int, matter_id: int) -> Matter: ...
    async def update(self, *, firm_id: int, matter_id: int, payload: UpdateMatterRequest) -> Matter: ...
    async def delete(self, *, firm_id: int, matter_id: int) -> None: ...


class ClientLookupPort(Protocol):
    async def get_for_firm(self, *, client_id: int, firm_id: int): ...


class MatterDocumentCleanupPort(Protocol):
    async def list_for_matter(self, *, matter_id: int, firm_id: int): ...


class MattersService:
    def __init__(
        self,
        repository: MattersRepository,
        clients_repository: ClientLookupPort,
        unit_of_work: UnitOfWorkPort,
        documents_repository: MatterDocumentCleanupPort,
        storage: FileStoragePort,
        storage_bucket: str,
    ):
        self.repository, self.clients_repository, self.unit_of_work = repository, clients_repository, unit_of_work
        self.documents_repository = documents_repository
        self.storage = storage
        self.storage_bucket = storage_bucket

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

    async def delete(self, *, firm_id: int, matter_id: int) -> None:
        async with self.unit_of_work:
            await self.get(firm_id=firm_id, matter_id=matter_id)
            documents = await self.documents_repository.list_for_matter(matter_id=matter_id, firm_id=firm_id)
            try:
                for document in documents:
                    await self.storage.delete(bucket=self.storage_bucket, path=document.storage_key)
            except FileStorageError as exc:
                raise InternalError("Matter deletion could not remove stored documents") from exc
            if not await self.repository.delete_scoped(matter_id=matter_id, firm_id=firm_id):
                raise NotFoundError("Matter not found")
