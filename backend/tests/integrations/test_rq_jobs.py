import asyncio
from types import SimpleNamespace

import pytest
from rq import Retry
from rq.exceptions import DuplicateJobError

from app.core.common.integration import EnqueueJobCommand
from app.core.config.settings import AIQueueSettings
from app.integrations.jobs import JobSchedulerError, UnsupportedJobError
from app.integrations.rq_jobs import RQJobScheduler


class Queue:
    def __init__(self, *, duplicate: bool = False) -> None:
        self.duplicate = duplicate
        self.calls: list[dict[str, object]] = []

    def enqueue_call(self, **kwargs):
        self.calls.append(kwargs)
        if self.duplicate:
            raise DuplicateJobError
        return SimpleNamespace(id=kwargs["job_id"])


def test_scheduler_enqueues_only_execution_id_with_resilience_policy() -> None:
    queue = Queue()
    settings = AIQueueSettings(
        AI_QUEUE_JOB_TIMEOUT_SECONDS=90,
        AI_QUEUE_MAX_RETRIES=3,
        AI_QUEUE_RETRY_BACKOFF_SECONDS="10,30,60",
        AI_QUEUE_RESULT_TTL_SECONDS=0,
        AI_QUEUE_FAILURE_TTL_SECONDS=600,
        AI_QUEUE_TTL_SECONDS=120,
    )
    scheduler = RQJobScheduler(
        settings=settings,
        handlers={"ai.execute": "app.features.example.worker"},
        queue=queue,
    )
    execution_id = "a" * 32

    result = asyncio.run(scheduler.enqueue(EnqueueJobCommand(job_name="ai.execute", execution_id=execution_id)))

    assert result == f"ai-{execution_id}"
    call = queue.calls[0]
    assert call["func"] == "app.features.example.worker"
    assert call["args"] == (execution_id,)
    assert call["job_id"] == f"ai-{execution_id}"
    assert call["unique"] is True
    assert call["timeout"] == 90
    assert call["ttl"] == 120
    assert call["result_ttl"] == 0
    assert call["failure_ttl"] == 600
    assert isinstance(call["retry"], Retry)
    assert "prompt" not in str(call).lower()
    assert "api_key" not in str(call).lower()


def test_scheduler_returns_deterministic_id_for_duplicate() -> None:
    execution_id = "b" * 32
    scheduler = RQJobScheduler(
        settings=AIQueueSettings(),
        handlers={"ai.execute": "app.features.example.worker"},
        queue=Queue(duplicate=True),
    )
    result = asyncio.run(scheduler.enqueue(EnqueueJobCommand(job_name="ai.execute", execution_id=execution_id)))
    assert result == f"ai-{execution_id}"


def test_scheduler_rejects_unknown_job_and_invalid_execution_id() -> None:
    scheduler = RQJobScheduler(
        settings=AIQueueSettings(),
        handlers={"ai.execute": "app.features.example.worker"},
        queue=Queue(),
    )
    with pytest.raises(UnsupportedJobError, match="Unsupported"):
        asyncio.run(scheduler.enqueue(EnqueueJobCommand(job_name="other", execution_id="a" * 32)))
    with pytest.raises(JobSchedulerError, match="identifier"):
        asyncio.run(scheduler.enqueue(EnqueueJobCommand(job_name="ai.execute", execution_id="unsafe")))


def test_scheduler_can_disable_retries() -> None:
    queue = Queue()
    scheduler = RQJobScheduler(
        settings=AIQueueSettings(AI_QUEUE_MAX_RETRIES=0),
        handlers={"ai.execute": "app.features.example.worker"},
        queue=queue,
    )
    asyncio.run(scheduler.enqueue(EnqueueJobCommand(job_name="ai.execute", execution_id="c" * 32)))
    assert queue.calls[0]["retry"] is None


def test_scheduler_wraps_queue_failures_without_provider_details() -> None:
    class FailingQueue(Queue):
        def enqueue_call(self, **kwargs):
            raise ConnectionError("redis://user:secret@private-host")  # pragma: allowlist secret

    scheduler = RQJobScheduler(
        settings=AIQueueSettings(),
        handlers={"ai.execute": "app.features.example.worker"},
        queue=FailingQueue(),
    )
    with pytest.raises(JobSchedulerError, match="dispatch failed") as error:
        asyncio.run(scheduler.enqueue(EnqueueJobCommand(job_name="ai.execute", execution_id="d" * 32)))
    assert "private-host" not in str(error.value)
