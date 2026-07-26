"""RQ adapter for safe, idempotent background AI job dispatch."""

import asyncio
import logging
from collections.abc import Mapping
from typing import Any, Protocol

from redis import Redis
from rq import Queue, Retry
from rq.exceptions import DuplicateJobError
from rq.serializers import JSONSerializer

from app.core.common.integration import EnqueueJobCommand
from app.core.common.observability import AiCorrelationContext, log_ai_event
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
        logger: logging.Logger | None = None,
    ):
        self.settings = settings
        self.handlers = dict(handlers)
        self.logger = logger or logging.getLogger("app.ai_queue")
        self.queue = queue or Queue(
            name=settings.AI_QUEUE_NAME,
            connection=Redis.from_url(settings.REDIS_URL),
            serializer=JSONSerializer,
            default_timeout=settings.AI_QUEUE_JOB_TIMEOUT_SECONDS,
        )

    async def enqueue(self, job: EnqueueJobCommand) -> str:
        try:
            correlation = AiCorrelationContext(
                request_id=job.request_id.strip(),
                execution_id=job.execution_id.strip(),
            )
        except ValueError as exc:
            raise JobSchedulerError("Invalid AI correlation identifier") from exc
        handler = self.handlers.get(job.job_name)
        if handler is None:
            raise UnsupportedJobError("Unsupported background job")
        execution_id = correlation.execution_id
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
            log_ai_event(
                self.logger,
                layer="ai_queue",
                event="ai_job_duplicate",
                correlation=correlation,
                job_name=job.job_name,
            )
            return rq_job_id
        except Exception as exc:
            log_ai_event(
                self.logger,
                layer="ai_queue",
                event="ai_job_enqueue_failed",
                correlation=correlation,
                job_name=job.job_name,
                error_type=type(exc).__name__,
                level=logging.ERROR,
            )
            raise JobSchedulerError("Background job dispatch failed") from exc
        log_ai_event(
            self.logger,
            layer="ai_queue",
            event="ai_job_enqueued",
            correlation=correlation,
            job_name=job.job_name,
        )
        return queued.id
