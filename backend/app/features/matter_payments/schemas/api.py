from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from app.core.common.schema import ApiSchema


def _validate_money(value: Decimal, *, positive: bool) -> Decimal:
    value = value.quantize(Decimal("0.01"))
    if value < 0 or (positive and value == 0):
        raise PydanticCustomError(
            "invalid_money", "amount must be positive" if positive else "amount must be nonnegative"
        )
    if value >= Decimal("1000000000000"):
        raise PydanticCustomError("money_too_large", "amount is too large")
    return value


class UpdateMatterBillingRequest(ApiSchema):
    agreed_fee: Decimal
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        value = value.strip() if value else None
        return value or None

    @field_validator("agreed_fee")
    @classmethod
    def validate_agreed_fee(cls, value: Decimal) -> Decimal:
        return _validate_money(value, positive=False)


class CreateMatterPaymentRequest(ApiSchema):
    amount: Decimal
    payment_type: Literal["advance", "partial"]
    paid_on: date
    note: str | None = Field(default=None, max_length=1000)

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        value = value.strip() if value else None
        return value or None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        return _validate_money(value, positive=True)


class MatterPaymentResponse(ApiSchema):
    id: int
    matter_id: int
    amount: Decimal
    payment_type: Literal["advance", "partial"]
    paid_on: date
    note: str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MatterBillingResponse(ApiSchema):
    matter_id: int
    currency: Literal["MXN"] = "MXN"
    agreed_fee: Decimal
    total_paid: Decimal
    balance: Decimal
    notes: str | None
    payments: list[MatterPaymentResponse]
