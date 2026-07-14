from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, Form, Response, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MatterDocumentsServiceDependency
from app.features.matter_documents.openapi import (
    CREATE_MATTER_DOCUMENT_DOC,
    DELETE_MATTER_DOCUMENT_DOC,
    DOWNLOAD_MATTER_DOCUMENT_DOC,
    LIST_MATTER_DOCUMENTS_DOC,
)
from app.features.matter_documents.schemas.api import DocumentType, MatterDocumentListResponse, MatterDocumentResponse

router = APIRouter(prefix="/matters/{matter_id}/documents", tags=["matter-documents"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated matter document users must belong to a firm")
    return user.firm_id


@router.post(
    "", response_model=MatterDocumentResponse, status_code=status.HTTP_201_CREATED, **CREATE_MATTER_DOCUMENT_DOC
)
async def upload_matter_document(
    matter_id: int,
    user: AuthenticatedReadAccessDependency,
    service: MatterDocumentsServiceDependency,
    document_type: Annotated[DocumentType, Form()],
    file: Annotated[UploadFile, File()],
):
    return await service.upload(firm_id=_firm_id(user), matter_id=matter_id, document_type=document_type, file=file)


@router.get("", response_model=MatterDocumentListResponse, **LIST_MATTER_DOCUMENTS_DOC)
async def list_matter_documents(
    matter_id: int, user: AuthenticatedReadAccessDependency, service: MatterDocumentsServiceDependency
):
    items, total = await service.list(firm_id=_firm_id(user), matter_id=matter_id)
    return MatterDocumentListResponse(items=items, total=total)


@router.get("/{document_id}/download", **DOWNLOAD_MATTER_DOCUMENT_DOC)
async def download_matter_document(
    matter_id: int, document_id: str, user: AuthenticatedReadAccessDependency, service: MatterDocumentsServiceDependency
):
    document, stream = await service.download(firm_id=_firm_id(user), matter_id=matter_id, document_id=document_id)
    disposition = f"attachment; filename*=UTF-8''{quote(document.original_filename)}"
    return StreamingResponse(stream, media_type=document.media_type, headers={"Content-Disposition": disposition})


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, **DELETE_MATTER_DOCUMENT_DOC)
async def delete_matter_document(
    matter_id: int, document_id: str, user: AuthenticatedReadAccessDependency, service: MatterDocumentsServiceDependency
):
    await service.delete(firm_id=_firm_id(user), matter_id=matter_id, document_id=document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
