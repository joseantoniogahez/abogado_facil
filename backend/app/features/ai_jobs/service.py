import logging
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from app.core.common.observability import AiCorrelationContext, log_ai_event
from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import ConflictError, InvalidInputError, NotFoundError
from app.features.ai_jobs.schemas import AIJobRecord, AIJobStatus, CreateAIJobCommand
from app.integrations.ai_outputs import ValidatedAIOutput


class AIJobsRepositoryPort(Protocol):
    async def create(self, **values: Any) -> AIJobRecord: ...

    async def get_scoped(
        self, *, execution_id: str, user_id: int, firm_id: int, for_update: bool = False
    ) -> AIJobRecord | None: ...

    async def update_scoped(
        self,
        *,
        execution_id: str,
        user_id: int,
        firm_id: int,
        status: str,
        attempt_count: int,
        result: dict[str, Any] | None,
        error_code: str | None,
        started_at: datetime | None,
        completed_at: datetime | None,
    ) -> AIJobRecord | None: ...


class AIJobsService:
    def __init__(
        self,
        repository: AIJobsRepositoryPort,
        unit_of_work: UnitOfWorkPort,
        logger: logging.Logger | None = None,
    ):
        self.repository = repository
        self.unit_of_work = unit_of_work
        self.logger = logger or logging.getLogger("app.ai_jobs")

    async def create(
        self,
        *,
        user_id: int,
        firm_id: int,
        command: CreateAIJobCommand,
        execution_id: str | None = None,
    ) -> AIJobRecord:
        async with self.unit_of_work:
            job = await self.repository.create(
                execution_id=execution_id or uuid4().hex,
                user_id=user_id,
                firm_id=firm_id,
                status=AIJobStatus.QUEUED.value,
                attempt_count=0,
                result=None,
                error_code=None,
                started_at=None,
                completed_at=None,
                **command.model_dump(),
            )
            self._log_lifecycle(job, event="ai_job_created")
            return job

    async def get(self, *, execution_id: str, user_id: int, firm_id: int) -> AIJobRecord:
        job = await self.repository.get_scoped(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
        if job is None:
            raise NotFoundError(message="AI job not found")
        return job

    async def start(self, *, execution_id: str, user_id: int, firm_id: int) -> AIJobRecord:
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            if job.status not in {AIJobStatus.QUEUED, AIJobStatus.FAILED}:
                raise ConflictError(message="AI job cannot be started from its current status")
            updated = await self._update(
                job,
                status=AIJobStatus.RUNNING,
                attempt_count=job.attempt_count + 1,
                started_at=datetime.now(UTC),
            )
            self._log_lifecycle(updated, event="ai_job_started")
            return updated

    async def succeed(
        self,
        *,
        execution_id: str,
        user_id: int,
        firm_id: int,
        result: ValidatedAIOutput,
    ) -> AIJobRecord:
        if not isinstance(result, ValidatedAIOutput):
            raise InvalidInputError(message="AI job result must be schema validated")
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            self._require_running(job)
            if result.schema_version != job.schema_version:
                raise InvalidInputError(message="AI output schema version does not match the job")
            updated = await self._update(
                job,
                status=AIJobStatus.SUCCEEDED,
                result=result.data,
                completed_at=datetime.now(UTC),
            )
            self._log_lifecycle(updated, event="ai_job_succeeded")
            return updated

    async def fail(self, *, execution_id: str, user_id: int, firm_id: int, error_code: str) -> AIJobRecord:
        if not error_code or len(error_code) > 100 or not error_code.replace("_", "").isalnum():
            raise InvalidInputError(message="AI job error code is invalid")
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            self._require_running(job)
            updated = await self._update(
                job,
                status=AIJobStatus.FAILED,
                error_code=error_code,
                completed_at=datetime.now(UTC),
            )
            self._log_lifecycle(updated, event="ai_job_failed")
            return updated

    async def cancel(self, *, execution_id: str, user_id: int, firm_id: int) -> AIJobRecord:
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            if job.status not in {AIJobStatus.QUEUED, AIJobStatus.RUNNING}:
                raise ConflictError(message="AI job cannot be cancelled from its current status")
            updated = await self._update(job, status=AIJobStatus.CANCELLED, completed_at=datetime.now(UTC))
            self._log_lifecycle(updated, event="ai_job_cancelled")
            return updated

    def _log_lifecycle(self, job: AIJobRecord, *, event: str) -> None:
        fields: dict[str, Any] = {
            "status": job.status.value if isinstance(job.status, AIJobStatus) else job.status,
            "attempt_count": job.attempt_count,
        }
        if job.error_code is not None:
            fields["error_code"] = job.error_code
        log_ai_event(
            self.logger,
            layer="ai_job",
            event=event,
            correlation=AiCorrelationContext(
                request_id=job.request_id,
                execution_id=job.execution_id,
            ),
            **fields,
        )

    @staticmethod
    def _require_running(job: AIJobRecord) -> None:
        if job.status != AIJobStatus.RUNNING:
            raise ConflictError(message="AI job is not running")

    async def _get_for_update(self, *, execution_id: str, user_id: int, firm_id: int) -> AIJobRecord:
        job = await self.repository.get_scoped(
            execution_id=execution_id,
            user_id=user_id,
            firm_id=firm_id,
            for_update=True,
        )
        if job is None:
            raise NotFoundError(message="AI job not found")
        return job

    async def _update(
        self,
        job: AIJobRecord,
        *,
        status: AIJobStatus,
        attempt_count: int | None = None,
        result: dict[str, Any] | None = None,
        error_code: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> AIJobRecord:
        updated = await self.repository.update_scoped(
            execution_id=job.execution_id,
            user_id=job.user_id,
            firm_id=job.firm_id,
            status=status.value,
            attempt_count=job.attempt_count if attempt_count is None else attempt_count,
            result=result,
            error_code=error_code,
            started_at=job.started_at if started_at is None else started_at,
            completed_at=completed_at,
        )
        if updated is None:
            raise NotFoundError(message="AI job not found")
        return updated
