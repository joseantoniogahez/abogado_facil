from fastapi import APIRouter, Response, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MatterNotesServiceDependency
from app.features.matter_notes.openapi import (
    CREATE_MATTER_NOTE_DOC,
    DELETE_MATTER_NOTE_DOC,
    LIST_MATTER_NOTES_DOC,
    UPDATE_MATTER_NOTE_DOC,
)
from app.features.matter_notes.schemas.api import (
    CreateMatterNoteRequest,
    MatterNoteListResponse,
    MatterNoteResponse,
    UpdateMatterNoteRequest,
)

router = APIRouter(prefix="/matters/{matter_id}/notes", tags=["matter-notes"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated matter note users must belong to a firm")
    return user.firm_id


@router.post("", response_model=MatterNoteResponse, status_code=status.HTTP_201_CREATED, **CREATE_MATTER_NOTE_DOC)
async def create_matter_note(
    matter_id: int,
    payload: CreateMatterNoteRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterNotesServiceDependency,
):
    return await service.create(firm_id=_firm_id(user), matter_id=matter_id, payload=payload)


@router.get("", response_model=MatterNoteListResponse, **LIST_MATTER_NOTES_DOC)
async def list_matter_notes(
    matter_id: int, user: AuthenticatedReadAccessDependency, service: MatterNotesServiceDependency
):
    items, total = await service.list(firm_id=_firm_id(user), matter_id=matter_id)
    return MatterNoteListResponse(items=items, total=total)


@router.patch("/{note_id}", response_model=MatterNoteResponse, **UPDATE_MATTER_NOTE_DOC)
async def update_matter_note(
    matter_id: int,
    note_id: int,
    payload: UpdateMatterNoteRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterNotesServiceDependency,
):
    return await service.update(firm_id=_firm_id(user), matter_id=matter_id, note_id=note_id, payload=payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, **DELETE_MATTER_NOTE_DOC)
async def delete_matter_note(
    matter_id: int, note_id: int, user: AuthenticatedReadAccessDependency, service: MatterNotesServiceDependency
):
    await service.delete(firm_id=_firm_id(user), matter_id=matter_id, note_id=note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
