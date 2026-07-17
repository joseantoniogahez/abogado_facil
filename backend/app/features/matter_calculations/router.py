from fastapi import APIRouter, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MatterCalculationsServiceDependency
from app.features.matter_calculations.schemas.api import (
    CalculateMatterRequest,
    MatterCalculationListResponse,
    MatterCalculationResponse,
)

router = APIRouter(prefix="/matters/{matter_id}/calculations", tags=["matter-calculations"])


def firm_id(user):
    if user.firm_id is None:
        raise ValueError("Matter calculation user must belong to a firm")
    return user.firm_id


@router.post("/preview", response_model=MatterCalculationResponse)
async def preview_calculation(
    matter_id: int,
    payload: CalculateMatterRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterCalculationsServiceDependency,
):
    return await service.calculate(firm_id(user), matter_id, payload)


@router.post("", response_model=MatterCalculationResponse, status_code=status.HTTP_201_CREATED)
async def save_calculation(
    matter_id: int,
    payload: CalculateMatterRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterCalculationsServiceDependency,
):
    return await service.save(firm_id(user), matter_id, payload)


@router.get("", response_model=MatterCalculationListResponse)
async def list_calculations(
    matter_id: int, user: AuthenticatedReadAccessDependency, service: MatterCalculationsServiceDependency
):
    return await service.list_saved(firm_id(user), matter_id)
