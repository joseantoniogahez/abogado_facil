from typing import Protocol

from app.features.dashboard.schemas.api import (
    DashboardAction,
    DashboardMetric,
    DashboardSummaryResponse,
    DashboardUpcomingTask,
)


class ClientCountPort(Protocol):
    async def count_for_firm(self, *, firm_id: int, search: str | None = None) -> int: ...


class MatterCountPort(Protocol):
    async def count_for_firm(self, *, firm_id: int, client_id: int | None = None, status: str | None = None) -> int: ...
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class TaskSummaryPort(Protocol):
    async def count_pending_for_firm(self, *, firm_id: int) -> int: ...
    async def list_upcoming_for_firm(self, *, firm_id: int, limit: int = 5): ...


class DashboardServicePort(Protocol):
    async def get_summary(self, *, firm_id: int, firm_name: str) -> DashboardSummaryResponse: ...


class DashboardService:
    def __init__(
        self,
        clients_repository: ClientCountPort,
        matters_repository: MatterCountPort,
        tasks_repository: TaskSummaryPort,
    ):
        self.clients_repository = clients_repository
        self.matters_repository = matters_repository
        self.tasks_repository = tasks_repository

    async def get_summary(self, *, firm_id: int, firm_name: str) -> DashboardSummaryResponse:
        client_count = await self.clients_repository.count_for_firm(firm_id=firm_id)
        active_matter_count = await self.matters_repository.count_for_firm(firm_id=firm_id, status="active")
        pending_task_count = await self.tasks_repository.count_pending_for_firm(firm_id=firm_id)
        upcoming_tasks = await self.tasks_repository.list_upcoming_for_firm(firm_id=firm_id, limit=5)
        upcoming_items = []
        for task in upcoming_tasks:
            matter = await self.matters_repository.get_for_firm(matter_id=task.matter_id, firm_id=firm_id)
            if matter is not None:
                upcoming_items.append(
                    DashboardUpcomingTask(
                        id=task.id,
                        matter_id=task.matter_id,
                        matter_title=matter.title,
                        title=task.title,
                        due_date=task.due_date,
                    )
                )
        return DashboardSummaryResponse(
            firm_id=firm_id,
            firm_name=firm_name,
            clients=DashboardMetric(value=client_count, available=True),
            active_matters=DashboardMetric(value=active_matter_count, available=True),
            pending_tasks=DashboardMetric(value=pending_task_count, available=True),
            upcoming_tasks=upcoming_items,
            ai_status="not_available",
            actions=[
                DashboardAction(id="create_client", available=True),
                DashboardAction(id="create_matter", available=True),
                DashboardAction(id="analyze_intake", available=False),
            ],
        )
