from datetime import date, datetime
from typing import Literal

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.core.common.schema import ApiSchema

MatterStatus = Literal["active", "pending", "closed"]


class MatterFields(ApiSchema):
    client_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    matter_type: str = Field(min_length=1, max_length=100)
    status: MatterStatus = "active"
    counterparty: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    next_action: str | None = Field(default=None, max_length=500)
    next_action_date: date | None = None

    @field_validator("title", "matter_type")
    @classmethod
    def required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("counterparty", "description", "next_action")
    @classmethod
    def optional_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class CreateMatterRequest(MatterFields):
    pass


class UpdateMatterRequest(ApiSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    matter_type: str | None = Field(default=None, min_length=1, max_length=100)
    status: MatterStatus | None = None
    counterparty: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    next_action: str | None = Field(default=None, max_length=500)
    next_action_date: date | None = None

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one field is required")
        return self


class MatterResponse(MatterFields):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MatterListResponse(ApiSchema):
    items: list[MatterResponse]
    total: int
    limit: int
    offset: int
