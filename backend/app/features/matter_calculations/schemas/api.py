from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.core.common.schema import ApiSchema

CalculationType = Literal["debt_balance", "overdue_rent", "simple_interest"]


class CalculateMatterRequest(ApiSchema):
    calculation_type: CalculationType
    principal: Decimal = Field(ge=0, lt=1000000000000)
    payments: Decimal = Field(ge=0, lt=1000000000000)
    monthly_rent: Decimal = Field(ge=0, lt=1000000000000)
    overdue_months: int = Field(ge=0, le=1200)
    annual_rate: Decimal = Field(ge=0, le=10000)
    days: int = Field(ge=0, le=36500)


class MatterCalculationResponse(ApiSchema):
    id: int | None = None
    matter_id: int
    calculation_type: CalculationType
    inputs: dict[str, str | int]
    result_amount: Decimal
    currency: Literal["MXN"] = "MXN"
    summary: str
    disclaimer: str
    created_at: datetime | None = None


class MatterCalculationListResponse(ApiSchema):
    items: list[MatterCalculationResponse]
