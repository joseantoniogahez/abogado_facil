"""RQ adapter for safe, idempotent background AI job dispatch."""

import asyncio
from collections.abc import Mapping
from typing import Any, Protocol

from redis import Redis
from rq import Queue, Retry
from rq.exceptions import DuplicateJobError
from rq.serializers import JSONSerializer

from app.core.common.integration import EnqueueJobCommand
from app.core.config.settings import AIQueueSettings
from app.integrations.jobs import JobSchedulerError, UnsupportedJobError


class QueueJob(Protocol):
    id: str


class QueuePort(Protocol):
    def enqueue_call(self, **kwargs: Any) -> QueueJob: ...


class RQJobScheduler:
    def __init__(
        self,
        *,
        settings: AIQueueSettings,
        handlers: Mapping[str, str],
        queue: QueuePort | None = None,
    ):
        self.settings = settings
        self.handlers = dict(handlers)
        self.queue = queue or Queue(
            name=settings.AI_QUEUE_NAME,
            connection=Redis.from_url(settings.REDIS_URL),
            serializer=JSONSerializer,
            default_timeout=settings.AI_QUEUE_JOB_TIMEOUT_SECONDS,
        )

    async def enqueue(self, job: EnqueueJobCommand) -> str:
        handler = self.handlers.get(job.job_name)
        if handler is None:
            raise UnsupportedJobError("Unsupported background job")
        execution_id = job.execution_id.strip()
        if len(execution_id) != 32 or any(character not in "0123456789abcdef" for character in execution_id):
            raise JobSchedulerError("Invalid AI execution identifier")

        rq_job_id = f"ai-{execution_id}"
        retry = None
        if self.settings.AI_QUEUE_MAX_RETRIES:
            retry = Retry(
                max=self.settings.AI_QUEUE_MAX_RETRIES,
                interval=self.settings.retry_backoff_seconds,
            )
        try:
            queued = await asyncio.to_thread(
                self.queue.enqueue_call,
                func=handler,
                args=(execution_id,),
                job_id=rq_job_id,
                unique=True,
                timeout=self.settings.AI_QUEUE_JOB_TIMEOUT_SECONDS,
                ttl=self.settings.AI_QUEUE_TTL_SECONDS,
                result_ttl=self.settings.AI_QUEUE_RESULT_TTL_SECONDS,
                failure_ttl=self.settings.AI_QUEUE_FAILURE_TTL_SECONDS,
                retry=retry,
                description=f"{job.job_name}:{execution_id}",
            )
        except DuplicateJobError:
            return rq_job_id
        except Exception as exc:
            raise JobSchedulerError("Background job dispatch failed") from exc
        return queued.id
