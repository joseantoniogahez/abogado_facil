from typing import Protocol

from app.core.common.integration import EnqueueJobCommand


class JobSchedulerPort(Protocol):
    async def enqueue(self, job: EnqueueJobCommand) -> str: ...


class JobSchedulerError(RuntimeError):
    """Provider-neutral queue failure without Redis or job payload details."""


class UnsupportedJobError(JobSchedulerError):
    """The requested internal handler is not registered."""
