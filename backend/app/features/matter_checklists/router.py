from fastapi import APIRouter, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MatterChecklistsServiceDependency
from app.features.matter_checklists.openapi import (
    CREATE_CHECKLIST_ITEM_DOC,
    LIST_CHECKLIST_DOC,
    UPDATE_CHECKLIST_ITEM_DOC,
)
from app.features.matter_checklists.schemas.api import (
    ChecklistItemResponse,
    ChecklistResponse,
    CreateChecklistItemRequest,
    UpdateChecklistItemRequest,
)

router = APIRouter(prefix="/matters/{matter_id}/checklist", tags=["matter-checklists"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated checklist users must belong to a firm")
    return user.firm_id


@router.get("", response_model=ChecklistResponse, **LIST_CHECKLIST_DOC)
async def list_matter_checklist(
    matter_id: int, user: AuthenticatedReadAccessDependency, service: MatterChecklistsServiceDependency
):
    items, total = await service.list(firm_id=_firm_id(user), matter_id=matter_id)
    return ChecklistResponse(items=items, total=total)


@router.post("", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED, **CREATE_CHECKLIST_ITEM_DOC)
async def create_checklist_item(
    matter_id: int,
    payload: CreateChecklistItemRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterChecklistsServiceDependency,
):
    return await service.create(firm_id=_firm_id(user), matter_id=matter_id, payload=payload)


@router.patch("/{item_id}", response_model=ChecklistItemResponse, **UPDATE_CHECKLIST_ITEM_DOC)
async def update_checklist_item(
    matter_id: int,
    item_id: int,
    payload: UpdateChecklistItemRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterChecklistsServiceDependency,
):
    return await service.update(firm_id=_firm_id(user), matter_id=matter_id, item_id=item_id, payload=payload)
