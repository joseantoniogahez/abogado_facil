from datetime import date, datetime

from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.core.common.schema import ApiSchema


class CreateMatterTaskRequest(ApiSchema):
    title: str = Field(min_length=1, max_length=500)
    due_date: date

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise PydanticCustomError("blank_title", "must not be blank")
        return value


class UpdateMatterTaskRequest(ApiSchema):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    due_date: date | None = None
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str:
        if value is None:
            raise PydanticCustomError("null_title", "must not be null")
        value = value.strip()
        if not value:
            raise PydanticCustomError("blank_title", "must not be blank")
        return value

    @field_validator("due_date")
    @classmethod
    def reject_null_due_date(cls, value: date | None) -> date:
        if value is None:
            raise PydanticCustomError("null_due_date", "must not be null")
        return value

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise PydanticCustomError("empty_update", "At least one field is required")
        return self


class MatterTaskResponse(ApiSchema):
    id: int
    matter_id: int
    title: str
    due_date: date
    completed: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MatterTaskListResponse(ApiSchema):
    items: list[MatterTaskResponse]
    total: int
