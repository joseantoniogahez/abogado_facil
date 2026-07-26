from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import ConfigDict, Field

from app.core.common.schema import ApplicationSchema


class AIJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreateAIJobCommand(ApplicationSchema):
    request_id: str = Field(min_length=1, max_length=100)
    feature: str = Field(min_length=1, max_length=100)
    provider: str = Field(min_length=1, max_length=30)
    model: str = Field(min_length=1, max_length=100)
    prompt_version: str = Field(min_length=1, max_length=50)
    schema_version: str = Field(min_length=1, max_length=50)


class AIJobRecord(ApplicationSchema):
    id: int
    execution_id: str
    request_id: str
    firm_id: int
    user_id: int
    feature: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    status: AIJobStatus
    attempt_count: int
    result: dict[str, Any] | None
    error_code: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(frozen=True, from_attributes=True)
