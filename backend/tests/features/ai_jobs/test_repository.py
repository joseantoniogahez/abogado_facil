import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.features.ai_jobs.models import AIJob
from app.features.ai_jobs.repository import AIJobsRepository


def job():
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=1,
        execution_id="a" * 32,
        request_id="request-1",
        firm_id=3,
        user_id=7,
        feature="initial-story",
        provider="openai",
        model="gpt-test",
        prompt_version="prompt-v1",
        schema_version="schema-v1",
        status="queued",
        attempt_count=0,
        result=None,
        error_code=None,
        started_at=None,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


def session_with(item):
    result = MagicMock()
    result.scalar_one_or_none.return_value = item
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


def test_create_get_and_update_are_scoped() -> None:
    async def run() -> None:
        persisted = job()
        session = session_with(persisted)
        repository = AIJobsRepository(session)
        repository._to_record = MagicMock(side_effect=lambda value: value)

        created = await repository.create(execution_id=persisted.execution_id)
        found = await repository.get_scoped(execution_id=persisted.execution_id, user_id=7, firm_id=3)
        locked = await repository.get_scoped(execution_id=persisted.execution_id, user_id=7, firm_id=3, for_update=True)
        updated = await repository.update_scoped(
            execution_id=persisted.execution_id,
            user_id=7,
            firm_id=3,
            status="running",
            attempt_count=1,
            result=None,
            error_code=None,
            started_at=datetime.now(UTC),
            completed_at=None,
        )

        assert created is not None
        assert found is persisted
        assert locked is persisted
        assert updated.status == "running"
        for call in session.execute.await_args_list:
            query = str(call.args[0])
            assert "ai_jobs.user_id" in query
            assert "ai_jobs.firm_id" in query
        assert session.flush.await_count == 2
        assert session.refresh.await_count == 2

    asyncio.run(run())


def test_missing_scoped_job_returns_none() -> None:
    async def run() -> None:
        repository = AIJobsRepository(session_with(None))
        assert await repository.get_scoped(execution_id="missing", user_id=7, firm_id=3) is None
        assert (
            await repository.update_scoped(
                execution_id="missing",
                user_id=7,
                firm_id=3,
                status="failed",
                attempt_count=1,
                result=None,
                error_code="safe_error",
                started_at=None,
                completed_at=datetime.now(UTC),
            )
            is None
        )

    asyncio.run(run())


def test_model_is_converted_to_immutable_record() -> None:
    persisted = job()
    record = AIJobsRepository._to_record(AIJob(**vars(persisted)))
    assert record.execution_id == persisted.execution_id
    assert record.status.value == "queued"
