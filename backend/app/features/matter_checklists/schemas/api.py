from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from app.core.common.schema import ApiSchema

ChecklistStatus = Literal["pending", "complete", "not_applicable"]


class CreateChecklistItemRequest(ApiSchema):
    label: str = Field(min_length=1, max_length=500)

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise PydanticCustomError("blank_label", "must not be blank")
        return value


class UpdateChecklistItemRequest(ApiSchema):
    status: ChecklistStatus


class ChecklistItemResponse(ApiSchema):
    id: int
    matter_id: int
    label: str
    status: ChecklistStatus
    is_custom: bool
    is_ai_suggested: bool
    position: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChecklistResponse(ApiSchema):
    items: list[ChecklistItemResponse]
    total: int
