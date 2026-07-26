import asyncio
from datetime import UTC, datetime
from typing import Any

import pytest

from app.core.errors.services import ConflictError, InvalidInputError, NotFoundError
from app.features.ai_jobs.schemas import AIJobRecord, AIJobStatus, CreateAIJobCommand
from app.features.ai_jobs.service import AIJobsService
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode


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
        service = AIJobsService(repository, uow)

        queued = await service.create(user_id=7, firm_id=3, command=command(), execution_id="a" * 32)
        assert queued.status == AIJobStatus.QUEUED
        assert queued.request_id == "request-1"
        assert queued.prompt_version == "prompt-v1"
        assert queued.schema_version == "schema-v1"
        assert await service.get(execution_id=queued.execution_id, user_id=7, firm_id=3) == queued

        running = await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        assert running.status == AIJobStatus.RUNNING
        assert running.attempt_count == 1
        assert running.started_at is not None

        succeeded = await service.succeed(
            execution_id=queued.execution_id,
            user_id=7,
            firm_id=3,
            result={"questions": ["safe structured output"]},
        )
        assert succeeded.status == AIJobStatus.SUCCEEDED
        assert succeeded.result == {"questions": ["safe structured output"]}
        assert succeeded.error_code is None
        assert succeeded.completed_at is not None
        assert uow.entries == 3

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
        with pytest.raises(ConflictError):
            await service.succeed(execution_id=queued.execution_id, user_id=7, firm_id=3, result={"ok": True})

        await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        with pytest.raises(ConflictError):
            await service.start(execution_id=queued.execution_id, user_id=7, firm_id=3)
        await service.succeed(execution_id=queued.execution_id, user_id=7, firm_id=3, result={"ok": True})
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
