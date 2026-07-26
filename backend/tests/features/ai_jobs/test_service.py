import asyncio
import logging
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.core.common.integration import EnqueueJobCommand
from app.core.config.settings import AIQueueSettings
from app.core.errors.services import ConflictError, InvalidInputError, NotFoundError
from app.features.ai_jobs.schemas import AIJobRecord, AIJobStatus, CreateAIJobCommand
from app.features.ai_jobs.service import AIJobsService
from app.integrations.ai_context import build_minimized_ai_context
from app.integrations.ai_outputs import ValidatedAIOutput
from app.integrations.ai_providers import (
    AiProviderError,
    AiProviderErrorCode,
    AiTextRequest,
    MockProvider,
)
from app.integrations.rq_jobs import RQJobScheduler


class Uow:
    def __init__(self) -> None:
        self.entries = 0

    async def __aenter__(self):
        self.entries += 1
        return self

    async def __aexit__(self, *_args):
        return False


class Repository:
    def __init__(self) -> None:
        self.jobs: dict[str, AIJobRecord] = {}

    async def create(self, **values: Any) -> AIJobRecord:
        now = datetime.now(UTC)
        job = AIJobRecord(id=1, created_at=now, updated_at=now, **values)
        self.jobs[job.execution_id] = job
        return job

    async def get_scoped(
        self, *, execution_id: str, user_id: int, firm_id: int, for_update: bool = False
    ) -> AIJobRecord | None:
        job = self.jobs.get(execution_id)
        if job is None or job.user_id != user_id or job.firm_id != firm_id:
            return None
        return job

    async def update_scoped(self, *, execution_id: str, user_id: int, firm_id: int, **values: Any):
        job = await self.get_scoped(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
        if job is None:
            return None
        updated = job.model_copy(update=values)
        self.jobs[execution_id] = updated
        return updated


def command() -> CreateAIJobCommand:
    return CreateAIJobCommand(
        request_id="request-1",
        feature="initial-story",
        provider="openai",
        model="gpt-test",
        prompt_version="prompt-v1",
        schema_version="schema-v1",
    )


def test_successful_lifecycle_tracks_correlation_versions_and_attempt() -> None:
    async def run() -> None:
        repository = Repository()
        uow = Uow()
        logger = MagicMock(spec=logging.Logger)
        service = AIJobsService(repository, uow, logger=logger)

        queued = await service.create(user_id=7, firm_id=3, command=command(), execution_id="a" * 32)
        assert queued.status == AIJobStatus.QUEUED
        assert queued.request_id == "request-1"
        assert queued.prompt_version == "prompt-v1"
        assert queued.schema_version == "schema-v1"
        assert await service.get(execution_id=queued.execution_id, user_id=7, firm_id=3) == queued

        class Queue:
            @staticmethod
            def enqueue_call(**values: Any) -> SimpleNamespace:
                return SimpleNamespace(id=values["job_id"])

        scheduler = RQJobScheduler(
            settings=AIQueueSettings(),
            handlers={"ai.execute": "app.features.example.worker"},
            queue=Queue(),
            logger=logger,
        )
        await scheduler.enqueue(
            EnqueueJobCommand(
                job_name="ai.execute",
                request_id=queued.request_id,
                execution_id=queued.execution_id,
            )
        )
        running = await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        assert running.status == AIJobStatus.RUNNING
        assert running.attempt_count == 1
        assert running.started_at is not None

        provider_response = await MockProvider(response="provider output", logger=logger).generate(
            AiTextRequest(
                context=build_minimized_ai_context(
                    instruction="Analyze",
                    source_context={"matter_text": "private prompt"},
                    authorized_fields={"matter_text"},
                    necessary_fields={"matter_text"},
                ),
                function=queued.feature,
                model=queued.model,
                request_id=queued.request_id,
                execution_id=queued.execution_id,
            )
        )
        assert provider_response.text == "provider output"

        succeeded = await service.succeed(
            execution_id=queued.execution_id,
            user_id=7,
            firm_id=3,
            result=ValidatedAIOutput(
                data={"questions": ["safe structured output"]},
                schema_version="schema-v1",
            ),
        )
        assert succeeded.status == AIJobStatus.SUCCEEDED
        assert succeeded.result == {"questions": ["safe structured output"]}
        assert succeeded.error_code is None
        assert succeeded.completed_at is not None
        assert uow.entries == 3
        log_text = " ".join(str(call) for call in logger.log.call_args_list)
        assert "ai_job_created" in log_text
        assert "ai_job_started" in log_text
        assert "ai_job_succeeded" in log_text
        assert "ai_job_enqueued" in log_text
        assert "ai_provider_started" in log_text
        assert "ai_provider_succeeded" in log_text
        assert queued.request_id in log_text
        assert queued.execution_id in log_text
        assert "private prompt" not in log_text
        assert "provider output" not in log_text
        assert "safe structured output" not in log_text

    asyncio.run(run())


def test_failure_can_be_started_as_new_attempt_and_cancelled() -> None:
    async def run() -> None:
        repository = Repository()
        service = AIJobsService(repository, Uow())
        queued = await service.create(user_id=7, firm_id=3, command=command())
        await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        provider_error = AiProviderError(AiProviderErrorCode.TIMEOUT)
        failed = await service.fail(
            execution_id=queued.execution_id,
            user_id=7,
            firm_id=3,
            error_code=provider_error.error_code,
        )
        assert failed.status == AIJobStatus.FAILED
        assert failed.error_code == "provider_timeout"
        assert failed.result is None

        retried = await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        assert retried.attempt_count == 2
        assert retried.error_code is None
        assert retried.completed_at is None
        cancelled = await service.cancel(execution_id=queued.execution_id, user_id=7, firm_id=3)
        assert cancelled.status == AIJobStatus.CANCELLED
        assert cancelled.completed_at is not None

    asyncio.run(run())


def test_missing_scoped_job_and_invalid_transitions_are_rejected() -> None:
    async def run() -> None:
        repository = Repository()
        service = AIJobsService(repository, Uow())
        queued = await service.create(user_id=7, firm_id=3, command=command())

        with pytest.raises(NotFoundError):
            await service.get(execution_id=queued.execution_id, user_id=8, firm_id=3)
        with pytest.raises(NotFoundError):
            await service.start(execution_id=queued.execution_id, user_id=8, firm_id=3)
        with pytest.raises(InvalidInputError):
            await service.fail(execution_id=queued.execution_id, user_id=7, firm_id=3, error_code="unsafe message")
        with pytest.raises(InvalidInputError, match="schema validated"):
            await service.succeed(
                execution_id=queued.execution_id,
                user_id=7,
                firm_id=3,
                result={"ok": True},  # type: ignore[arg-type]
            )
        with pytest.raises(ConflictError):
            await service.succeed(
                execution_id=queued.execution_id,
                user_id=7,
                firm_id=3,
                result=ValidatedAIOutput(data={"ok": True}, schema_version="schema-v1"),
            )

        await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        with pytest.raises(ConflictError):
            await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        with pytest.raises(InvalidInputError, match="schema version"):
            await service.succeed(
                execution_id=queued.execution_id,
                user_id=7,
                firm_id=3,
                result=ValidatedAIOutput(data={"ok": True}, schema_version="schema-v2"),
            )
        await service.succeed(
            execution_id=queued.execution_id,
            user_id=7,
            firm_id=3,
            result=ValidatedAIOutput(data={"ok": True}, schema_version="schema-v1"),
        )
        with pytest.raises(ConflictError):
            await service.cancel(execution_id=queued.execution_id, user_id=7, firm_id=3)

        original_update = repository.update_scoped

        async def missing_update(**_values):
            return None

        repository.update_scoped = missing_update
        running = repository.jobs[queued.execution_id].model_copy(update={"status": AIJobStatus.RUNNING})
        with pytest.raises(NotFoundError):
            await service._update(running, status=AIJobStatus.CANCELLED)
        repository.update_scoped = original_update

    asyncio.run(run())
