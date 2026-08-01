from typing import Literal

from pydantic import Field, field_validator

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
    generation_available: bool = True


class DocumentDraftInput(ApiSchema):
    template_key: DocumentTemplateKey
    fields: dict[str, str] = Field(min_length=1, max_length=20)
    provider: Literal["openai", "gemini"]
    model: str = Field(min_length=1, max_length=100)

    @field_validator("fields")
    @classmethod
    def strip_fields(cls, values: dict[str, str]) -> dict[str, str]:
        return {key: value.strip() for key, value in values.items()}

    @field_validator("model")
    @classmethod
    def strip_model(cls, value: str) -> str:
        return value.strip()


class DocumentDraftPreviewRequest(DocumentDraftInput):
    pass


class DocumentDraftPreviewResponse(ApiSchema):
    template_key: DocumentTemplateKey
    provider: str
    model: str
    included_fields: list[str]
    character_count: int
    estimated_max_output_tokens: int
    cost_notice: str
    confirmation_token: str


class GenerateDocumentDraftRequest(DocumentDraftInput):
    confirmation_token: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")


class DocumentDraftResponse(ApiSchema):
    template_key: DocumentTemplateKey
    content: str
    provider: str
    model: str
    execution_id: str
    status: Literal["draft"] = "draft"
    requires_professional_review: Literal[True] = True
