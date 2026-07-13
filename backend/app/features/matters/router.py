from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MattersServiceDependency
from app.features.matters.openapi import CREATE_MATTER_DOC, GET_MATTER_DOC, LIST_MATTERS_DOC, UPDATE_MATTER_DOC
from app.features.matters.schemas.api import (
    CreateMatterRequest,
    MatterListResponse,
    MatterResponse,
    UpdateMatterRequest,
)

router = APIRouter(prefix="/matters", tags=["matters"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated matter users must belong to a firm")
    return user.firm_id


@router.post("", response_model=MatterResponse, status_code=status.HTTP_201_CREATED, **CREATE_MATTER_DOC)
async def create_matter(
    payload: CreateMatterRequest, user: AuthenticatedReadAccessDependency, service: MattersServiceDependency
):
    return await service.create(firm_id=_firm_id(user), payload=payload)


@router.get("", response_model=MatterListResponse, **LIST_MATTERS_DOC)
async def list_matters(
    user: AuthenticatedReadAccessDependency,
    service: MattersServiceDependency,
    client_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = await service.list(firm_id=_firm_id(user), client_id=client_id, limit=limit, offset=offset)
    return MatterListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{matter_id}", response_model=MatterResponse, **GET_MATTER_DOC)
async def get_matter(matter_id: int, user: AuthenticatedReadAccessDependency, service: MattersServiceDependency):
    return await service.get(firm_id=_firm_id(user), matter_id=matter_id)


@router.patch("/{matter_id}", response_model=MatterResponse, **UPDATE_MATTER_DOC)
async def update_matter(
    matter_id: int,
    payload: UpdateMatterRequest,
    user: AuthenticatedReadAccessDependency,
    service: MattersServiceDependency,
):
    return await service.update(firm_id=_firm_id(user), matter_id=matter_id, payload=payload)
