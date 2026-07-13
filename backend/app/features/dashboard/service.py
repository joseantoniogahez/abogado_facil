from typing import Protocol

from app.features.dashboard.schemas.api import DashboardAction, DashboardMetric, DashboardSummaryResponse


class ClientCountPort(Protocol):
    async def count_for_firm(self, *, firm_id: int, search: str | None = None) -> int: ...


class MatterCountPort(Protocol):
    async def count_for_firm(self, *, firm_id: int, client_id: int | None = None, status: str | None = None) -> int: ...


class DashboardServicePort(Protocol):
    async def get_summary(self, *, firm_id: int, firm_name: str) -> DashboardSummaryResponse: ...


class DashboardService:
    def __init__(self, clients_repository: ClientCountPort, matters_repository: MatterCountPort):
        self.clients_repository = clients_repository
        self.matters_repository = matters_repository

    async def get_summary(self, *, firm_id: int, firm_name: str) -> DashboardSummaryResponse:
        unavailable_metric = DashboardMetric(value=0, available=False)
        client_count = await self.clients_repository.count_for_firm(firm_id=firm_id)
        active_matter_count = await self.matters_repository.count_for_firm(firm_id=firm_id, status="active")
        return DashboardSummaryResponse(
            firm_id=firm_id,
            firm_name=firm_name,
            clients=DashboardMetric(value=client_count, available=True),
            active_matters=DashboardMetric(value=active_matter_count, available=True),
            pending_tasks=unavailable_metric,
            upcoming_tasks=[],
            ai_status="not_available",
            actions=[
                DashboardAction(id="create_client", available=True),
                DashboardAction(id="create_matter", available=True),
                DashboardAction(id="analyze_intake", available=False),
            ],
        )
