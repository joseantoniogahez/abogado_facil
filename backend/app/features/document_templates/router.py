from fastapi import APIRouter

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.features.document_templates.catalog import DOCUMENT_TEMPLATES
from app.features.document_templates.openapi import LIST_DOCUMENT_TEMPLATES_DOC
from app.features.document_templates.schemas.api import (
    DocumentTemplateFieldResponse,
    DocumentTemplateListResponse,
    DocumentTemplateResponse,
)

router = APIRouter(prefix="/document-templates", tags=["document-templates"])


@router.get("", response_model=DocumentTemplateListResponse, **LIST_DOCUMENT_TEMPLATES_DOC)
async def list_document_templates(user: AuthenticatedReadAccessDependency):
    del user
    return DocumentTemplateListResponse(
        items=[
            DocumentTemplateResponse(
                key=template.key,
                name=template.name,
                description=template.description,
                purpose=template.purpose,
                fields=[
                    DocumentTemplateFieldResponse(
                        key=field.key,
                        label=field.label,
                        field_type=field.field_type,
                        required=field.required,
                    )
                    for field in template.fields
                ],
            )
            for template in DOCUMENT_TEMPLATES
        ]
    )
