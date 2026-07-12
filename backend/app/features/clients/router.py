from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import ClientsServiceDependency
from app.features.clients.openapi import CREATE_CLIENT_DOC, GET_CLIENT_DOC, LIST_CLIENTS_DOC, UPDATE_CLIENT_DOC
from app.features.clients.schemas.api import (
    ClientListResponse,
    ClientResponse,
    CreateClientRequest,
    UpdateClientRequest,
)

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated client users must belong to a firm")
    return user.firm_id


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, **CREATE_CLIENT_DOC)
async def create_client(
    payload: CreateClientRequest, user: AuthenticatedReadAccessDependency, service: ClientsServiceDependency
):
    return await service.create(firm_id=_firm_id(user), payload=payload)


@router.get("", response_model=ClientListResponse, **LIST_CLIENTS_DOC)
async def list_clients(
    user: AuthenticatedReadAccessDependency,
    service: ClientsServiceDependency,
    search: Annotated[str | None, Query(max_length=255)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = await service.list(firm_id=_firm_id(user), search=search, limit=limit, offset=offset)
    return ClientListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{client_id}", response_model=ClientResponse, **GET_CLIENT_DOC)
async def get_client(client_id: int, user: AuthenticatedReadAccessDependency, service: ClientsServiceDependency):
    return await service.get(firm_id=_firm_id(user), client_id=client_id)


@router.patch("/{client_id}", response_model=ClientResponse, **UPDATE_CLIENT_DOC)
async def update_client(
    client_id: int,
    payload: UpdateClientRequest,
    user: AuthenticatedReadAccessDependency,
    service: ClientsServiceDependency,
):
    return await service.update(firm_id=_firm_id(user), client_id=client_id, payload=payload)
