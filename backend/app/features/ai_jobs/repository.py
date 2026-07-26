from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.ai_jobs.models import AIJob
from app.features.ai_jobs.schemas import AIJobRecord


class AIJobsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_record(job: AIJob) -> AIJobRecord:
        return AIJobRecord.model_validate(job)

    async def create(self, **values: Any) -> AIJobRecord:
        job = AIJob(**values)
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return self._to_record(job)

    async def get_scoped(
        self, *, execution_id: str, user_id: int, firm_id: int, for_update: bool = False
    ) -> AIJobRecord | None:
        query = select(AIJob).where(
            AIJob.execution_id == execution_id,
            AIJob.user_id == user_id,
            AIJob.firm_id == firm_id,
        )
        if for_update:
            query = query.with_for_update()
        job = (await self.session.execute(query)).scalar_one_or_none()
        return None if job is None else self._to_record(job)

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
    ) -> AIJobRecord | None:
        query = select(AIJob).where(
            AIJob.execution_id == execution_id,
            AIJob.user_id == user_id,
            AIJob.firm_id == firm_id,
        )
        job = (await self.session.execute(query)).scalar_one_or_none()
        if job is None:
            return None
        job.status = status
        job.attempt_count = attempt_count
        job.result = result
        job.error_code = error_code
        job.started_at = started_at
        job.completed_at = completed_at
        await self.session.flush()
        await self.session.refresh(job)
        return self._to_record(job)
