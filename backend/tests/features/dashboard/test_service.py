import asyncio
from unittest.mock import AsyncMock

from app.features.dashboard.service import DashboardService


def test_dashboard_service_returns_deterministic_unavailable_summary() -> None:
    async def run_test() -> None:
        repository = AsyncMock()
        repository.count_for_firm.return_value = 4
        result = await DashboardService(repository).get_summary(firm_id=17, firm_name="Despacho Norte")

        assert result.firm_id == 17
        assert result.firm_name == "Despacho Norte"
        assert result.clients.value == 4
        assert result.clients.available is True
        assert result.active_matters.available is False
        assert result.pending_tasks.available is False
        assert result.upcoming_tasks == []
        assert result.ai_status == "not_available"
        assert result.actions[0].available is True
        assert all(action.available is False for action in result.actions[1:])

    asyncio.run(run_test())
