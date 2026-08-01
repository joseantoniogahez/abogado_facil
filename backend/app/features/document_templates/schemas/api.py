from typing import Literal

from app.core.common.schema import ApiSchema
from app.features.document_templates.catalog import DocumentTemplateFieldType, DocumentTemplateKey


class DocumentTemplateFieldResponse(ApiSchema):
    key: str
    label: str
    field_type: DocumentTemplateFieldType
    required: bool


class DocumentTemplateResponse(ApiSchema):
    key: DocumentTemplateKey
    name: str
    description: str
    purpose: str
    fields: list[DocumentTemplateFieldResponse]


class DocumentTemplateListResponse(ApiSchema):
    items: list[DocumentTemplateResponse]
    generation_available: Literal[False] = False
