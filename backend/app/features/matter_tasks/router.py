from fastapi import APIRouter, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MatterTasksServiceDependency
from app.features.matter_tasks.openapi import CREATE_MATTER_TASK_DOC, LIST_MATTER_TASKS_DOC, UPDATE_MATTER_TASK_DOC
from app.features.matter_tasks.schemas.api import (
    CreateMatterTaskRequest,
    MatterTaskListResponse,
    MatterTaskResponse,
    UpdateMatterTaskRequest,
)

router = APIRouter(prefix="/matters/{matter_id}/tasks", tags=["matter-tasks"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated matter task users must belong to a firm")
    return user.firm_id


@router.get("", response_model=MatterTaskListResponse, **LIST_MATTER_TASKS_DOC)
async def list_matter_tasks(
    matter_id: int, user: AuthenticatedReadAccessDependency, service: MatterTasksServiceDependency
):
    items, total = await service.list(firm_id=_firm_id(user), matter_id=matter_id)
    return MatterTaskListResponse(items=items, total=total)


@router.post("", response_model=MatterTaskResponse, status_code=status.HTTP_201_CREATED, **CREATE_MATTER_TASK_DOC)
async def create_matter_task(
    matter_id: int,
    payload: CreateMatterTaskRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterTasksServiceDependency,
):
    return await service.create(firm_id=_firm_id(user), matter_id=matter_id, payload=payload)


@router.patch("/{task_id}", response_model=MatterTaskResponse, **UPDATE_MATTER_TASK_DOC)
async def update_matter_task(
    matter_id: int,
    task_id: int,
    payload: UpdateMatterTaskRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterTasksServiceDependency,
):
    return await service.update(firm_id=_firm_id(user), matter_id=matter_id, task_id=task_id, payload=payload)
