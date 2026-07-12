from datetime import datetime

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.core.common.schema import ApiSchema

MEXICO_COUNTRY_CODE = "52"
MEXICO_PHONE_DIGITS = 10


def normalize_mexico_phone(value: str) -> str:
    digits = "".join(character for character in value if character in "0123456789")
    if len(digits) == MEXICO_PHONE_DIGITS + len(MEXICO_COUNTRY_CODE) and digits.startswith(MEXICO_COUNTRY_CODE):
        digits = digits[len(MEXICO_COUNTRY_CODE) :]
    if len(digits) != MEXICO_PHONE_DIGITS:
        raise ValueError("phone must contain exactly 10 Mexican national digits")
    return digits


class ClientFields(ApiSchema):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=32)
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    address: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=10000)

    @field_validator("full_name")
    @classmethod
    def strip_required(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_mexico_phone(value)

    @field_validator("address", "notes")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class CreateClientRequest(ClientFields):
    pass


class UpdateClientRequest(ApiSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=1, max_length=32)
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    address: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=10000)

    @field_validator("full_name")
    @classmethod
    def strip_required(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        return normalize_mexico_phone(value) if value is not None else None

    @model_validator(mode="after")
    def require_change(self):
        if not self.model_fields_set:
            raise ValueError("At least one field is required")
        return self


class ClientResponse(ClientFields):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(ApiSchema):
    items: list[ClientResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
