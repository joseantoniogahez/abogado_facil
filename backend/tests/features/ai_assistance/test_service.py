import asyncio
import json
from datetime import UTC, date, datetime
from functools import wraps
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from app.core.errors.services import ConflictError, InvalidInputError, NotFoundError
from app.features.ai_assistance.repository import AIAssistanceRepository
from app.features.ai_assistance.schemas import (
    ConvertAIAssistanceRequest,
    ExecuteAIAssistanceRequest,
    ReviewAIAssistanceRequest,
)
from app.features.ai_assistance.service import AIAssistanceService
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode, AiTextResponse

_DEFAULT = object()


def run_async(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))

    return wrapper


class Uow:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


def matter(description: str | None = "Descripción") -> SimpleNamespace:
    return SimpleNamespace(id=3, description=description, updated_at=datetime.now(UTC))


def item(status: str = "pending") -> SimpleNamespace:
    return SimpleNamespace(
        id=9,
        feature="intake_analysis",
        review_status=status,
        converted_actions=[],
        source_snapshot={"matter_updated_at": datetime.now(UTC).isoformat()},
    )


def payload(feature: str = "intake_analysis") -> ExecuteAIAssistanceRequest:
    return ExecuteAIAssistanceRequest(
        feature=feature,
        narrative="Relato suficientemente largo para analizar.",
        provider="openai",
        model="model",
        include_matter_description=True,
        confirmation_token="a" * 64,
    )


def service(*, found_matter=_DEFAULT, found_result=_DEFAULT, provider_text: str | None = None):
    if found_matter is _DEFAULT:
        found_matter = matter()
    if found_result is _DEFAULT:
        found_result = item()
    repository = SimpleNamespace(
        create=AsyncMock(side_effect=lambda **values: SimpleNamespace(id=1, **values)),
        list_scoped=AsyncMock(return_value=[found_result]),
        count_scoped=AsyncMock(return_value=1),
        get_scoped=AsyncMock(return_value=found_result),
        update_result=AsyncMock(side_effect=lambda result, **values: SimpleNamespace(**(vars(result) | values))),
    )
    matters = SimpleNamespace(get_for_firm=AsyncMock(return_value=found_matter))
    if provider_text is None:
        provider_text = json.dumps(
            {
                "summary": "Resumen",
                "relevant_facts": ["Hecho"],
                "critical_data": [],
                "missing_documents": [],
                "next_steps": [],
            }
        )
    provider = SimpleNamespace(
        generate=AsyncMock(return_value=AiTextResponse(provider="openai", model="model", text=provider_text))
    )
    factory = SimpleNamespace(build=AsyncMock(return_value=provider))
    job = SimpleNamespace(execution_id="e" * 32)
    jobs = SimpleNamespace(
        create=AsyncMock(return_value=job),
        start=AsyncMock(),
        succeed=AsyncMock(),
        fail=AsyncMock(),
    )
    notes = SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(id=41)))
    tasks = SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(id=42)))
    checklists = SimpleNamespace(
        create=AsyncMock(return_value=SimpleNamespace(id=43)),
        count_for_matter=AsyncMock(return_value=4),
    )
    return (
        AIAssistanceService(
            cast(AIAssistanceRepository, repository),
            matters,
            factory,
            jobs,
            Uow(),
            preview_signing_key="test-preview-signing-key",
            notes_repository=notes,
            tasks_repository=tasks,
            checklists_repository=checklists,
        ),
        repository,
        matters,
        factory,
        jobs,
    )


@run_async
async def test_preview_lists_included_and_excluded_sources() -> None:
    subject, *_ = service()
    result = await subject.preview(matter_id=3, firm_id=2, payload=payload())
    assert result.included_sources == ["relato proporcionado", "descripción del asunto"]
    assert result.character_count > 20
    without_description = payload().model_copy(update={"include_matter_description": False})
    result = await subject.preview(matter_id=3, firm_id=2, payload=without_description)
    assert "descripción del asunto" in result.excluded_sources


@run_async
async def test_missing_matter_is_opaque() -> None:
    subject, _, _, factory, jobs = service(found_matter=None)
    with pytest.raises(NotFoundError):
        await subject.preview(matter_id=3, firm_id=2, payload=payload())
    with pytest.raises(NotFoundError):
        await subject.execute(
            matter_id=3,
            firm_id=2,
            user_id=1,
            request_id="req",
            payload=payload(),
        )
    factory.build.assert_not_awaited()
    jobs.create.assert_not_awaited()


@run_async
async def test_foreign_result_cannot_be_used_as_regeneration_source() -> None:
    subject, repository, _, factory, jobs = service()
    repository.get_scoped.return_value = None
    command = payload().model_copy(update={"regenerates_result_id": 999})
    with pytest.raises(NotFoundError):
        await subject.preview(matter_id=3, firm_id=2, payload=command)
    repository.get_scoped.assert_awaited_once_with(result_id=999, matter_id=3, firm_id=2)
    factory.build.assert_not_awaited()
    jobs.create.assert_not_awaited()


@run_async
async def test_regeneration_rejects_a_different_feature() -> None:
    prior = item("accepted")
    subject, _, *_ = service(found_result=prior)
    command = payload("client_questions").model_copy(update={"regenerates_result_id": prior.id})
    with pytest.raises(ConflictError):
        await subject.preview(matter_id=3, firm_id=2, payload=command)


@pytest.mark.parametrize(
    ("feature", "response"),
    [
        ("intake_analysis", {"summary": "S", "relevant_facts": ["F"]}),
        ("client_questions", {"questions": ["¿Qué ocurrió?"]}),
        ("client_message", {"channel": "whatsapp", "subject": None, "message": "Mensaje"}),
        (
            "matter_summary",
            {
                "summary": "Resumen ejecutivo",
                "matter_status": "En integración",
                "key_facts": ["Contrato firmado"],
                "pending_items": ["Recibir anexos"],
                "next_steps": ["Revisar anexos"],
            },
        ),
    ],
)
@run_async
async def test_execute_validates_each_feature_and_persists_result(feature: str, response: dict) -> None:
    subject, repository, _, factory, jobs = service(provider_text=json.dumps(response))
    command = payload(feature)
    preview = await subject.preview(matter_id=3, firm_id=2, payload=command)
    command = command.model_copy(update={"confirmation_token": preview.confirmation_token})
    result = await subject.execute(matter_id=3, firm_id=2, user_id=1, request_id="req", payload=command)
    assert result.feature == feature
    assert result.review_status == "pending"
    factory.build.assert_awaited_once()
    jobs.start.assert_awaited_once()
    jobs.succeed.assert_awaited_once()
    repository.create.assert_awaited_once()
    request = factory.build.return_value.generate.await_args.args[0]
    context_fields = dict(request.context.fields)
    assert set(context_fields) == {"narrative", "matter_description"}
    assert "notas" not in context_fields
    assert "documentos" not in context_fields


@run_async
async def test_execute_records_normalized_provider_failure() -> None:
    subject, _, _, factory, jobs = service()
    factory.build.return_value.generate.side_effect = AiProviderError(AiProviderErrorCode.TIMEOUT)
    command = payload()
    preview = await subject.preview(matter_id=3, firm_id=2, payload=command)
    with pytest.raises(AiProviderError):
        await subject.execute(
            matter_id=3,
            firm_id=2,
            user_id=1,
            request_id="req",
            payload=command.model_copy(update={"confirmation_token": preview.confirmation_token}),
        )
    jobs.fail.assert_awaited_once()


@run_async
async def test_execute_rejects_payload_that_does_not_match_preview() -> None:
    subject, _, _, factory, _ = service()
    command = payload()
    preview = await subject.preview(matter_id=3, firm_id=2, payload=command)
    changed = command.model_copy(
        update={
            "narrative": "Un relato diferente que no fue confirmado por el usuario.",
            "confirmation_token": preview.confirmation_token,
        }
    )
    with pytest.raises(ConflictError):
        await subject.execute(matter_id=3, firm_id=2, user_id=1, request_id="req", payload=changed)
    factory.build.assert_not_awaited()


@run_async
async def test_regeneration_is_scoped_and_records_provenance() -> None:
    prior = item("accepted")
    subject, repository, *_ = service(found_result=prior)
    command = payload().model_copy(update={"regenerates_result_id": prior.id})
    preview = await subject.preview(matter_id=3, firm_id=2, payload=command)
    regenerated = await subject.execute(
        matter_id=3,
        firm_id=2,
        user_id=1,
        request_id="req",
        payload=command.model_copy(update={"confirmation_token": preview.confirmation_token}),
    )
    assert regenerated.source_snapshot["regenerates_result_id"] == prior.id
    repository.get_scoped.assert_awaited()


@run_async
async def test_list_review_and_convert_enforce_scope_and_acceptance() -> None:
    subject, repository, _, factory, _ = service()
    results, total = await subject.list(matter_id=3, firm_id=2)
    assert len(results) == total == 1
    factory.build.assert_not_awaited()
    reviewed = await subject.review(
        result_id=9,
        matter_id=3,
        firm_id=2,
        payload=ReviewAIAssistanceRequest(
            status="accepted",
            content={"summary": "Editado", "relevant_facts": ["Hecho confirmado"]},
        ),
    )
    assert reviewed.review_status == "accepted"
    with pytest.raises(InvalidInputError):
        await subject.review(
            result_id=9,
            matter_id=3,
            firm_id=2,
            payload=ReviewAIAssistanceRequest(status="accepted", content={"unexpected": "shape"}),
        )
    repository.get_scoped.return_value = None
    with pytest.raises(NotFoundError):
        await subject.review(
            result_id=9,
            matter_id=3,
            firm_id=2,
            payload=ReviewAIAssistanceRequest(status="rejected"),
        )
    with pytest.raises(NotFoundError):
        await subject.convert(
            result_id=9,
            matter_id=3,
            firm_id=2,
            payload=ConvertAIAssistanceRequest(action_type="note", content="Texto"),
        )

    repository.get_scoped.return_value = item()
    with pytest.raises(ConflictError):
        await subject.convert(
            result_id=9,
            matter_id=3,
            firm_id=2,
            payload=ConvertAIAssistanceRequest(action_type="note", content="Texto"),
        )
    repository.get_scoped.return_value = item("accepted")
    converted = await subject.convert(
        result_id=9,
        matter_id=3,
        firm_id=2,
        payload=ConvertAIAssistanceRequest(action_type="note", content="Texto"),
    )
    assert converted.converted_actions == [
        {
            "action_type": "note",
            "content": "Texto",
            "entity_id": 41,
            "entity_type": "note",
        }
    ]
    repository.get_scoped.return_value = item("accepted")
    converted_task = await subject.convert(
        result_id=9,
        matter_id=3,
        firm_id=2,
        payload=ConvertAIAssistanceRequest(
            action_type="task",
            content="Dar seguimiento",
            due_date=date(2026, 8, 15),
        ),
    )
    assert converted_task.converted_actions[0]["entity_id"] == 42
    repository.get_scoped.return_value = item("accepted")
    converted_checklist = await subject.convert(
        result_id=9,
        matter_id=3,
        firm_id=2,
        payload=ConvertAIAssistanceRequest(action_type="checklist", content="Obtener identificación"),
    )
    assert converted_checklist.converted_actions[0]["entity_id"] == 43


def test_request_contracts_reject_unconfirmed_or_inconsistent_review() -> None:
    with pytest.raises(ValidationError):
        payload().model_validate(payload().model_dump() | {"confirmation_token": "invalid"})
    with pytest.raises(ValidationError):
        ReviewAIAssistanceRequest(status="accepted")
    with pytest.raises(ValidationError):
        ReviewAIAssistanceRequest(status="rejected", content={"x": "y"})
    assert ConvertAIAssistanceRequest(action_type="note", content="  text  ").content == "text"
    with pytest.raises(ValidationError):
        ConvertAIAssistanceRequest(action_type="task", content="Sin fecha")
    with pytest.raises(ValidationError):
        ConvertAIAssistanceRequest(
            action_type="note",
            content="Con fecha indebida",
            due_date=date(2026, 8, 15),
        )
