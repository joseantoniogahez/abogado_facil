import asyncio
from unittest.mock import AsyncMock

from app.features.dashboard.service import DashboardService


def test_dashboard_service_returns_task_summary() -> None:
    async def run_test() -> None:
        repository = AsyncMock()
        repository.count_for_firm.return_value = 4
        matters_repository = AsyncMock()
        matters_repository.count_for_firm.return_value = 2
        tasks_repository = AsyncMock()
        tasks_repository.count_pending_for_firm.return_value = 3
        tasks_repository.list_upcoming_for_firm.return_value = []
        result = await DashboardService(repository, matters_repository, tasks_repository).get_summary(
            firm_id=17, firm_name="Despacho Norte"
        )

        assert result.firm_id == 17
        assert result.firm_name == "Despacho Norte"
        assert result.clients.value == 4
        assert result.clients.available is True
        assert result.active_matters.value == 2
        assert result.active_matters.available is True
        assert result.pending_tasks.value == 3
        assert result.pending_tasks.available is True
        assert result.upcoming_tasks == []
        assert result.ai_status == "not_available"
        assert result.actions[0].available is True
        assert result.actions[1].available is True
        assert result.actions[2].available is False

    asyncio.run(run_test())
