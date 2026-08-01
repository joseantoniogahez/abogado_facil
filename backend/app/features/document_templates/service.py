import hmac
import json
from hashlib import sha256
from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.core.common.schema import ApplicationSchema
from app.core.errors.services import ConflictError, InvalidInputError
from app.features.document_templates.catalog import DocumentTemplate, document_template_for
from app.features.document_templates.schemas.api import (
    DocumentDraftInput,
    DocumentDraftPreviewResponse,
    DocumentDraftResponse,
)
from app.integrations.ai_context import build_minimized_ai_context
from app.integrations.ai_outputs import validate_ai_output
from app.integrations.ai_providers import AiProviderError, AiTextRequest

PROMPT_VERSION = "document-draft-v1"
SCHEMA_VERSION = "document-draft-v1"


class DraftOutput(BaseModel):
    content: str = Field(min_length=1, max_length=30000)


class CreateDocumentDraftJobCommand(ApplicationSchema):
    request_id: str
    feature: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str


class ProviderFactoryPort(Protocol):
    async def build(self, *, user_id: int, firm_id: int, provider: str, model: str): ...


class JobsServicePort(Protocol):
    async def create(self, *, user_id: int, firm_id: int, command: Any): ...
    async def start(self, *, execution_id: str, user_id: int, firm_id: int): ...
    async def succeed(self, *, execution_id: str, user_id: int, firm_id: int, result: Any): ...
    async def fail(self, *, execution_id: str, user_id: int, firm_id: int, error_code: str): ...


class DocumentTemplatesService:
    def __init__(
        self,
        *,
        provider_factory: ProviderFactoryPort,
        jobs_service: JobsServicePort,
        preview_signing_key: str,
    ) -> None:
        self.provider_factory = provider_factory
        self.jobs_service = jobs_service
        self.preview_signing_key = preview_signing_key.encode()

    @staticmethod
    def _validated_fields(payload: DocumentDraftInput) -> tuple[DocumentTemplate, dict[str, str]]:
        template = document_template_for(payload.template_key)
        if template is None:
            raise InvalidInputError("Document template is not supported")
        expected = {field.key: field for field in template.fields}
        unknown = set(payload.fields) - expected.keys()
        if unknown:
            raise InvalidInputError("Document draft contains unknown fields")
        missing = [field.key for field in template.fields if field.required and not payload.fields.get(field.key, "")]
        if missing:
            raise InvalidInputError("Document draft is missing required fields")
        values = {key: value for key, value in payload.fields.items() if value}
        if any(len(value) > 20000 for value in values.values()):
            raise InvalidInputError("Document draft field exceeds the allowed size")
        return template, values

    def _confirmation_token(self, *, firm_id: int, payload: DocumentDraftInput, values: dict[str, str]) -> str:
        material = json.dumps(
            {
                "firm_id": firm_id,
                "template_key": payload.template_key,
                "fields": values,
                "provider": payload.provider,
                "model": payload.model,
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hmac.new(self.preview_signing_key, material.encode(), sha256).hexdigest()

    def preview(self, *, firm_id: int, payload: DocumentDraftInput) -> DocumentDraftPreviewResponse:
        template, values = self._validated_fields(payload)
        labels = {field.key: field.label for field in template.fields}
        return DocumentDraftPreviewResponse(
            template_key=template.key,
            provider=payload.provider,
            model=payload.model,
            included_fields=[labels[key] for key in values],
            character_count=sum(len(value) for value in values.values()),
            estimated_max_output_tokens=1800,
            cost_notice="El proveedor usará tu clave BYOK; revisa el borrador antes de utilizarlo.",
            confirmation_token=self._confirmation_token(firm_id=firm_id, payload=payload, values=values),
        )

    async def generate(
        self,
        *,
        firm_id: int,
        user_id: int,
        request_id: str,
        payload: DocumentDraftInput,
        confirmation_token: str,
    ) -> DocumentDraftResponse:
        template, values = self._validated_fields(payload)
        expected = self._confirmation_token(firm_id=firm_id, payload=payload, values=values)
        if not hmac.compare_digest(confirmation_token, expected):
            raise ConflictError("Document draft preview is stale; preview the current inputs again")
        instruction = (
            f"Redacta un {template.name} simple en español de México. Finalidad: {template.purpose} "
            "Usa solamente los datos aportados, conserva marcadores claros cuando falte información opcional, "
            "no inventes hechos ni citas legales, no prometas resultados y devuelve JSON con content."
        )
        context = build_minimized_ai_context(
            instruction=instruction,
            source_context=values,
            authorized_fields=set(values),
            necessary_fields=set(values),
        )
        feature = f"document_draft.{template.key}"
        job = await self.jobs_service.create(
            user_id=user_id,
            firm_id=firm_id,
            command=CreateDocumentDraftJobCommand(
                request_id=request_id,
                feature=feature,
                provider=payload.provider,
                model=payload.model,
                prompt_version=PROMPT_VERSION,
                schema_version=SCHEMA_VERSION,
            ),
        )
        await self.jobs_service.start(execution_id=job.execution_id, user_id=user_id, firm_id=firm_id)
        try:
            provider = await self.provider_factory.build(
                user_id=user_id,
                firm_id=firm_id,
                provider=payload.provider,
                model=payload.model,
            )
            response = await provider.generate(
                AiTextRequest(
                    context=context,
                    function="document_draft",
                    model=payload.model,
                    request_id=request_id,
                    execution_id=job.execution_id,
                    max_tokens=1800,
                    response_json_schema=DraftOutput.model_json_schema(),
                )
            )
            validated = validate_ai_output(response.text, schema=DraftOutput, schema_version=SCHEMA_VERSION)
        except AiProviderError as exc:
            await self.jobs_service.fail(
                execution_id=job.execution_id,
                user_id=user_id,
                firm_id=firm_id,
                error_code=exc.error_code,
            )
            raise
        await self.jobs_service.succeed(
            execution_id=job.execution_id,
            user_id=user_id,
            firm_id=firm_id,
            result=validated,
        )
        return DocumentDraftResponse(
            template_key=template.key,
            content=str(validated.data["content"]),
            provider=payload.provider,
            model=payload.model,
            execution_id=job.execution_id,
        )
