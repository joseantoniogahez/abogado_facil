from datetime import datetime
from enum import StrEnum

from pydantic import ConfigDict

from app.core.common.schema import ApiSchema


class DocumentType(StrEnum):
    IDENTIFICATION = "identification"
    RECORD = "record"
    CONTRACT = "contract"
    RECEIPT = "receipt"
    PROOF = "proof"
    FILING = "filing"
    NOTIFICATION = "notification"
    EVIDENCE = "evidence"
    OTHER = "other"


class MatterDocumentResponse(ApiSchema):
    id: str
    matter_id: int
    original_filename: str
    document_type: DocumentType
    media_type: str
    size_bytes: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MatterDocumentListResponse(ApiSchema):
    items: list[MatterDocumentResponse]
    total: int
