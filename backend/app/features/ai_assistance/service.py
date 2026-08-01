import datetime as dt
import hmac
import json
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Protocol

from pydantic import BaseModel, Field, ValidationError, model_validator

from app.core.common.schema import ApplicationSchema
from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import ConflictError, InvalidInputError, NotFoundError
from app.features.ai_assistance.repository import AIAssistanceRepository
from app.features.ai_assistance.schemas import (
    AIContextPreviewRequest,
    AIContextPreviewResponse,
    ConvertAIAssistanceRequest,
    ExecuteAIAssistanceRequest,
    ReviewAIAssistanceRequest,
)
from app.integrations.ai_context import build_minimized_ai_context
from app.integrations.ai_outputs import validate_ai_output
from app.integrations.ai_providers import AiProviderError, AiTextRequest

PROMPT_VERSION = "phase3-v1"
SCHEMA_VERSION = "phase3-v1"


class IntakeAnalysis(BaseModel):
    summary: str = Field(min_length=1, max_length=4000)
    relevant_facts: list[str] = Field(min_length=1, max_length=20)
    critical_data: list[str] = Field(default_factory=list, max_length=20)
    missing_documents: list[str] = Field(default_factory=list, max_length=20)
    next_steps: list[str] = Field(default_factory=list, max_length=20)


class ClientQuestions(BaseModel):
    questions: list[str] = Field(min_length=1, max_length=30)
    critical_data: list[str] = Field(default_factory=list, max_length=20)
    missing_documents: list[str] = Field(default_factory=list, max_length=20)


class ClientMessage(BaseModel):
    channel: str = Field(pattern=r"^(whatsapp|email)$")
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=1, max_length=8000)


class MatterSummary(BaseModel):
    summary: str = Field(min_length=1, max_length=5000)
    matter_status: str = Field(min_length=1, max_length=1000)
    key_facts: list[str] = Field(default_factory=list, max_length=30)
    pending_items: list[str] = Field(default_factory=list, max_length=30)
    next_steps: list[str] = Field(default_factory=list, max_length=30)


class TimelineEvent(BaseModel):
    date: dt.date | None = None
    description: str = Field(min_length=1, max_length=2000)
    source: str | None = Field(default=None, max_length=500)


class MatterTimeline(BaseModel):
    events: list[TimelineEvent] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def order_events(self):
        self.events.sort(key=lambda event: (event.date is None, event.date or "", event.description))
        return self


class ChecklistSuggestions(BaseModel):
    suggestions: list[str] = Field(min_length=1, max_length=30)


FEATURE_SCHEMAS: dict[str, type[BaseModel]] = {
    "intake_analysis": IntakeAnalysis,
    "client_questions": ClientQuestions,
    "client_message": ClientMessage,
    "matter_summary": MatterSummary,
    "matter_timeline": MatterTimeline,
    "checklist_suggestions": ChecklistSuggestions,
}
FEATURE_INSTRUCTIONS = {
    "intake_analysis": (
        "Analiza el relato para apoyar la organización inicial de un expediente mexicano. "
        "No des asesoría definitiva. Devuelve JSON con summary, relevant_facts, critical_data, "
        "missing_documents y next_steps."
    ),
    "client_questions": (
        "Genera preguntas neutrales para completar el relato del cliente. Devuelve JSON con "
        "questions, critical_data y missing_documents. No inventes hechos."
    ),
    "client_message": (
        "Redacta un mensaje profesional y prudente para solicitar información al cliente. "
        "Devuelve JSON con channel (whatsapp o email), subject y message. No prometas resultados."
    ),
    "matter_summary": (
        "Resume el expediente con lenguaje neutral y verificable para consulta interna. Devuelve "
        "JSON con summary, matter_status, key_facts, pending_items y next_steps. Distingue hechos "
        "aportados de pendientes, no inventes información y no des asesoría definitiva."
    ),
    "matter_timeline": (
        "Construye una cronología interna únicamente con hechos aportados. Devuelve JSON con events; "
        "cada evento contiene date en formato YYYY-MM-DD o null, description y source o null. No "
        "inventes fechas: usa null cuando no exista una fecha verificable e identifica la fuente "
        "aportada cuando esté disponible."
    ),
    "checklist_suggestions": (
        "Sugiere elementos adicionales para personalizar el checklist del expediente sin repetir "
        "el checklist base. Devuelve JSON con suggestions, una lista breve y accionable. No "
        "marques elementos como completos y no inventes requisitos legales."
    ),
}


class MatterLookupPort(Protocol):
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class ProviderFactoryPort(Protocol):
    async def build(self, *, user_id: int, firm_id: int, provider: str, model: str): ...


class JobsServicePort(Protocol):
    async def create(self, *, user_id: int, firm_id: int, command: Any): ...
    async def start(self, *, execution_id: str, user_id: int, firm_id: int): ...
    async def succeed(self, *, execution_id: str, user_id: int, firm_id: int, result: Any): ...
    async def fail(self, *, execution_id: str, user_id: int, firm_id: int, error_code: str): ...


class DerivedActionRepositoryPort(Protocol):
    async def create(self, **values): ...


class ChecklistActionRepositoryPort(DerivedActionRepositoryPort, Protocol):
    async def count_for_matter(self, *, matter_id: int, firm_id: int) -> int: ...


class CreateJobCommand(ApplicationSchema):
    request_id: str
    feature: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str


class AIAssistanceService:
    def __init__(
        self,
        repository: AIAssistanceRepository,
        matters_repository: MatterLookupPort,
        provider_factory: ProviderFactoryPort,
        jobs_service: JobsServicePort,
        unit_of_work: UnitOfWorkPort,
        preview_signing_key: str,
        notes_repository: DerivedActionRepositoryPort,
        tasks_repository: DerivedActionRepositoryPort,
        checklists_repository: ChecklistActionRepositoryPort,
    ):
        self.repository = repository
        self.matters_repository = matters_repository
        self.provider_factory = provider_factory
        self.jobs_service = jobs_service
        self.unit_of_work = unit_of_work
        self.preview_signing_key = preview_signing_key.encode()
        self.notes_repository = notes_repository
        self.tasks_repository = tasks_repository
        self.checklists_repository = checklists_repository

    def _confirmation_token(
        self,
        *,
        matter_id: int,
        firm_id: int,
        feature: str,
        provider: str,
        model: str,
        include_matter_description: bool,
        source_version: str,
        regenerates_result_id: int | None,
    ) -> str:
        material = json.dumps(
            {
                "matter_id": matter_id,
                "firm_id": firm_id,
                "feature": feature,
                "provider": provider,
                "model": model,
                "include_matter_description": include_matter_description,
                "source_version": source_version,
                "regenerates_result_id": regenerates_result_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hmac.new(self.preview_signing_key, material.encode(), sha256).hexdigest()

    async def _matter(self, *, matter_id: int, firm_id: int):
        matter = await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id)
        if matter is None:
            raise NotFoundError("Matter not found")
        return matter

    async def _sources(self, *, matter_id: int, firm_id: int, payload: AIContextPreviewRequest):
        matter = await self._matter(matter_id=matter_id, firm_id=firm_id)
        if payload.regenerates_result_id is not None:
            prior = await self.repository.get_scoped(
                result_id=payload.regenerates_result_id,
                matter_id=matter_id,
                firm_id=firm_id,
            )
            if prior is None:
                raise NotFoundError("AI result to regenerate not found")
            if prior.feature != payload.feature:
                raise ConflictError("Regeneration must use the same AI feature")
        fields = {"narrative": payload.narrative}
        included = ["relato proporcionado"]
        excluded = ["notas", "documentos", "pagos", "tareas"]
        if payload.include_matter_description and matter.description and matter.description.strip():
            fields["matter_description"] = matter.description.strip()
            included.append("descripción del asunto")
        else:
            excluded.append("descripción del asunto")
        version_material = json.dumps(
            {"matter_updated_at": matter.updated_at.isoformat(), "fields": fields},
            sort_keys=True,
            ensure_ascii=False,
        )
        return matter, fields, included, excluded, sha256(version_material.encode()).hexdigest()

    async def preview(
        self, *, matter_id: int, firm_id: int, payload: AIContextPreviewRequest
    ) -> AIContextPreviewResponse:
        _, fields, included, excluded, source_version = await self._sources(
            matter_id=matter_id, firm_id=firm_id, payload=payload
        )
        return AIContextPreviewResponse(
            feature=payload.feature,
            provider=payload.provider,
            model=payload.model,
            included_sources=included,
            excluded_sources=excluded,
            character_count=sum(len(value) for value in fields.values()),
            estimated_max_output_tokens=1200,
            cost_notice="El costo depende del proveedor, modelo y longitud final; se usará tu clave BYOK.",
            confirmation_token=self._confirmation_token(
                matter_id=matter_id,
                firm_id=firm_id,
                feature=payload.feature,
                provider=payload.provider,
                model=payload.model,
                include_matter_description=payload.include_matter_description,
                source_version=source_version,
                regenerates_result_id=payload.regenerates_result_id,
            ),
        )

    async def execute(
        self,
        *,
        matter_id: int,
        firm_id: int,
        user_id: int,
        request_id: str,
        payload: ExecuteAIAssistanceRequest,
    ):
        matter, fields, _, _, source_version = await self._sources(
            matter_id=matter_id, firm_id=firm_id, payload=payload
        )
        expected_confirmation = self._confirmation_token(
            matter_id=matter_id,
            firm_id=firm_id,
            feature=payload.feature,
            provider=payload.provider,
            model=payload.model,
            include_matter_description=payload.include_matter_description,
            source_version=source_version,
            regenerates_result_id=payload.regenerates_result_id,
        )
        if not hmac.compare_digest(payload.confirmation_token, expected_confirmation):
            raise ConflictError("Context preview is stale; preview the current inputs again")
        context = build_minimized_ai_context(
            instruction=FEATURE_INSTRUCTIONS[payload.feature],
            source_context=fields,
            authorized_fields=set(fields),
            necessary_fields=set(fields),
        )
        job = await self.jobs_service.create(
            user_id=user_id,
            firm_id=firm_id,
            command=CreateJobCommand(
                request_id=request_id,
                feature=payload.feature,
                provider=payload.provider,
                model=payload.model,
                prompt_version=PROMPT_VERSION,
                schema_version=SCHEMA_VERSION,
            ),
        )
        await self.jobs_service.start(execution_id=job.execution_id, user_id=user_id, firm_id=firm_id)
        try:
            provider = await self.provider_factory.build(
                user_id=user_id, firm_id=firm_id, provider=payload.provider, model=payload.model
            )
            response = await provider.generate(
                AiTextRequest(
                    context=context,
                    function=payload.feature,
                    model=payload.model,
                    request_id=request_id,
                    execution_id=job.execution_id,
                    max_tokens=1200,
                    response_json_schema=FEATURE_SCHEMAS[payload.feature].model_json_schema(),
                )
            )
            validated = validate_ai_output(
                response.text, schema=FEATURE_SCHEMAS[payload.feature], schema_version=SCHEMA_VERSION
            )
        except AiProviderError as exc:
            await self.jobs_service.fail(
                execution_id=job.execution_id,
                user_id=user_id,
                firm_id=firm_id,
                error_code=exc.error_code,
            )
            raise
        await self.jobs_service.succeed(
            execution_id=job.execution_id, user_id=user_id, firm_id=firm_id, result=validated
        )
        async with self.unit_of_work:
            result = await self.repository.create(
                firm_id=firm_id,
                matter_id=matter_id,
                user_id=user_id,
                execution_id=job.execution_id,
                feature=payload.feature,
                provider=payload.provider,
                model=payload.model,
                source_version=source_version,
                source_snapshot={
                    "fields": list(fields),
                    "prompt_version": PROMPT_VERSION,
                    "matter_updated_at": matter.updated_at.isoformat(),
                    "regenerates_result_id": payload.regenerates_result_id,
                },
                generated_content=validated.data,
                reviewed_content=None,
                review_status="pending",
                problem_report=None,
                converted_actions=[],
                reviewed_at=None,
            )
            result.is_stale = False
            return result

    async def list(self, *, matter_id: int, firm_id: int):
        matter = await self._matter(matter_id=matter_id, firm_id=firm_id)
        items = await self.repository.list_scoped(matter_id=matter_id, firm_id=firm_id)
        for item in items:
            item.is_stale = item.source_snapshot.get("matter_updated_at") != matter.updated_at.isoformat()
        return items, await self.repository.count_scoped(matter_id=matter_id, firm_id=firm_id)

    async def review(self, *, result_id: int, matter_id: int, firm_id: int, payload: ReviewAIAssistanceRequest):
        async with self.unit_of_work:
            item = await self.repository.get_scoped(result_id=result_id, matter_id=matter_id, firm_id=firm_id)
            if item is None:
                raise NotFoundError("AI result not found")
            reviewed_content = payload.content
            if payload.status in {"accepted", "partially_accepted"}:
                try:
                    reviewed_content = (
                        FEATURE_SCHEMAS[item.feature].model_validate(payload.content).model_dump(mode="json")
                    )
                except (KeyError, ValidationError) as exc:
                    raise InvalidInputError("Reviewed content does not match the AI feature schema") from exc
            result = await self.repository.update_result(
                item,
                review_status=payload.status,
                reviewed_content=reviewed_content,
                problem_report=payload.problem_report,
                reviewed_at=datetime.now(UTC),
            )
            result.is_stale = False
            return result

    async def convert(self, *, result_id: int, matter_id: int, firm_id: int, payload: ConvertAIAssistanceRequest):
        async with self.unit_of_work:
            item = await self.repository.get_scoped(result_id=result_id, matter_id=matter_id, firm_id=firm_id)
            if item is None:
                raise NotFoundError("AI result not found")
            if item.review_status not in {"accepted", "partially_accepted"}:
                raise ConflictError("AI result must be accepted before conversion")
            action = payload.model_dump(mode="json", exclude_none=True)
            if payload.action_type in {"note", "question", "message"}:
                prefixes = {
                    "note": "",
                    "question": "Pregunta para cliente:\n",
                    "message": "Mensaje para cliente:\n",
                }
                created = await self.notes_repository.create(
                    firm_id=firm_id,
                    matter_id=matter_id,
                    content=f"{prefixes[payload.action_type]}{payload.content}",
                    is_relevant=False,
                )
                action["entity_id"] = created.id
                action["entity_type"] = "note"
            elif payload.action_type == "task":
                created = await self.tasks_repository.create(
                    firm_id=firm_id,
                    matter_id=matter_id,
                    title=payload.content[:500],
                    due_date=payload.due_date,
                    completed=False,
                )
                action["entity_id"] = created.id
                action["entity_type"] = "task"
            elif payload.action_type in {"checklist", "missing_document"}:
                position = await self.checklists_repository.count_for_matter(
                    matter_id=matter_id,
                    firm_id=firm_id,
                )
                labels = (
                    [line.strip() for line in payload.content.splitlines() if line.strip()]
                    if item.feature == "checklist_suggestions" and payload.action_type == "checklist"
                    else [
                        payload.content
                        if payload.action_type == "checklist"
                        else f"Solicitar documento: {payload.content}"
                    ]
                )
                created_items = []
                for offset, label in enumerate(labels):
                    created_items.append(
                        await self.checklists_repository.create(
                            firm_id=firm_id,
                            matter_id=matter_id,
                            label=label[:500],
                            position=position + offset,
                            is_custom=True,
                            is_ai_suggested=True,
                        )
                    )
                action["entity_id"] = created_items[0].id
                action["entity_ids"] = [created.id for created in created_items]
                action["entity_type"] = "checklist"
            actions = [*item.converted_actions, action]
            result = await self.repository.update_result(item, converted_actions=actions)
            result.is_stale = False
            return result
