from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import ConflictError, InvalidInputError, NotFoundError
from app.features.ai_jobs.schemas import AIJobRecord, AIJobStatus, CreateAIJobCommand


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
    def __init__(self, repository: AIJobsRepositoryPort, unit_of_work: UnitOfWorkPort):
        self.repository = repository
        self.unit_of_work = unit_of_work

    async def create(
        self,
        *,
        user_id: int,
        firm_id: int,
        command: CreateAIJobCommand,
        execution_id: str | None = None,
    ) -> AIJobRecord:
        async with self.unit_of_work:
            return await self.repository.create(
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
            return await self._update(
                job,
                status=AIJobStatus.RUNNING,
                attempt_count=job.attempt_count + 1,
                started_at=datetime.now(UTC),
            )

    async def succeed(self, *, execution_id: str, user_id: int, firm_id: int, result: dict[str, Any]) -> AIJobRecord:
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            self._require_running(job)
            return await self._update(
                job,
                status=AIJobStatus.SUCCEEDED,
                result=result,
                completed_at=datetime.now(UTC),
            )

    async def fail(self, *, execution_id: str, user_id: int, firm_id: int, error_code: str) -> AIJobRecord:
        if not error_code or len(error_code) > 100 or not error_code.replace("_", "").isalnum():
            raise InvalidInputError(message="AI job error code is invalid")
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            self._require_running(job)
            return await self._update(
                job,
                status=AIJobStatus.FAILED,
                error_code=error_code,
                completed_at=datetime.now(UTC),
            )

    async def cancel(self, *, execution_id: str, user_id: int, firm_id: int) -> AIJobRecord:
        async with self.unit_of_work:
            job = await self._get_for_update(execution_id=execution_id, user_id=user_id, firm_id=firm_id)
            if job.status not in {AIJobStatus.QUEUED, AIJobStatus.RUNNING}:
                raise ConflictError(message="AI job cannot be cancelled from its current status")
            return await self._update(job, status=AIJobStatus.CANCELLED, completed_at=datetime.now(UTC))

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
