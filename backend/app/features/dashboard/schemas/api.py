from typing import Literal

from pydantic import Field

from app.core.common.schema import ApiSchema


class DashboardMetric(ApiSchema):
    value: int = Field(ge=0)
    available: bool


class DashboardAction(ApiSchema):
    id: Literal["create_client", "create_matter", "analyze_intake"]
    available: bool


class DashboardSummaryResponse(ApiSchema):
    firm_id: int
    firm_name: str
    clients: DashboardMetric
    active_matters: DashboardMetric
    pending_tasks: DashboardMetric
    upcoming_tasks: list[object]
    ai_status: Literal["not_available", "not_configured", "configured", "error"]
    actions: list[DashboardAction]
