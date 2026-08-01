from datetime import date, datetime
from typing import Any, Literal

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.core.common.schema import ApiSchema

AiFeature = Literal[
    "intake_analysis",
    "client_questions",
    "client_message",
    "matter_summary",
    "matter_timeline",
    "checklist_suggestions",
]
ReviewStatus = Literal["pending", "accepted", "partially_accepted", "rejected"]
ActionType = Literal["note", "task", "question", "checklist", "missing_document", "message"]


class AIContextPreviewRequest(ApiSchema):
    feature: AiFeature
    narrative: str = Field(min_length=20, max_length=20000)
    provider: Literal["openai", "gemini"]
    model: str = Field(min_length=1, max_length=100)
    include_matter_description: bool = True
    regenerates_result_id: int | None = Field(default=None, gt=0)

    @field_validator("narrative", "model")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class AIContextPreviewResponse(ApiSchema):
    feature: AiFeature
    provider: str
    model: str
    included_sources: list[str]
    excluded_sources: list[str]
    character_count: int
    estimated_max_output_tokens: int
    cost_notice: str
    confirmation_token: str


class ExecuteAIAssistanceRequest(AIContextPreviewRequest):
    confirmation_token: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")


class ReviewAIAssistanceRequest(ApiSchema):
    status: ReviewStatus
    content: dict[str, Any] | None = None
    problem_report: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_review(self):
        if self.status in {"accepted", "partially_accepted"} and not self.content:
            raise ValueError("Reviewed content is required for acceptance")
        if self.status == "rejected" and self.content is not None:
            raise ValueError("Rejected content cannot be accepted")
        return self


class ConvertAIAssistanceRequest(ApiSchema):
    action_type: ActionType
    content: str = Field(min_length=1, max_length=20000)
    due_date: date | None = None

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def require_task_due_date(self):
        if self.action_type == "task" and self.due_date is None:
            raise ValueError("Task conversion requires a due date")
        if self.action_type != "task" and self.due_date is not None:
            raise ValueError("Due date is only valid for task conversion")
        return self


class AIAssistanceResultResponse(ApiSchema):
    id: int
    matter_id: int
    execution_id: str
    feature: AiFeature
    provider: str
    model: str
    source_version: str
    source_snapshot: dict[str, Any]
    generated_content: dict[str, Any]
    reviewed_content: dict[str, Any] | None
    review_status: ReviewStatus
    problem_report: str | None
    converted_actions: list[dict[str, Any]]
    is_stale: bool
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIAssistanceResultListResponse(ApiSchema):
    items: list[AIAssistanceResultResponse]
    total: int
