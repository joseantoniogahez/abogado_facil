from datetime import datetime

from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.core.common.schema import ApiSchema


class CreateMatterNoteRequest(ApiSchema):
    content: str = Field(min_length=1, max_length=20000)
    is_relevant: bool = False

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise PydanticCustomError("blank_content", "must not be blank")
        return value


class UpdateMatterNoteRequest(ApiSchema):
    content: str | None = Field(default=None, min_length=1, max_length=20000)
    is_relevant: bool | None = None

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str | None) -> str | None:
        if value is None:
            raise PydanticCustomError("null_content", "must not be null")
        value = value.strip()
        if not value:
            raise PydanticCustomError("blank_content", "must not be blank")
        return value

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise PydanticCustomError("empty_update", "At least one field is required")
        return self


class MatterNoteResponse(ApiSchema):
    id: int
    matter_id: int
    content: str
    is_relevant: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MatterNoteListResponse(ApiSchema):
    items: list[MatterNoteResponse]
    total: int
