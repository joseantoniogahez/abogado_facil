from typing import Protocol

from app.features.dashboard.schemas.api import DashboardAction, DashboardMetric, DashboardSummaryResponse


class DashboardServicePort(Protocol):
    async def get_summary(self, *, firm_id: int, firm_name: str) -> DashboardSummaryResponse: ...


class DashboardService:
    async def get_summary(self, *, firm_id: int, firm_name: str) -> DashboardSummaryResponse:
        unavailable_metric = DashboardMetric(value=0, available=False)
        return DashboardSummaryResponse(
            firm_id=firm_id,
            firm_name=firm_name,
            clients=unavailable_metric,
            active_matters=unavailable_metric,
            pending_tasks=unavailable_metric,
            upcoming_tasks=[],
            ai_status="not_available",
            actions=[
                DashboardAction(id="create_client", available=False),
                DashboardAction(id="create_matter", available=False),
                DashboardAction(id="analyze_intake", available=False),
            ],
        )
