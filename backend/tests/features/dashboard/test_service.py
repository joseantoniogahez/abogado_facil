import asyncio

from app.features.dashboard.service import DashboardService


def test_dashboard_service_returns_deterministic_unavailable_summary() -> None:
    async def run_test() -> None:
        result = await DashboardService().get_summary(firm_id=17, firm_name="Despacho Norte")

        assert result.firm_id == 17
        assert result.firm_name == "Despacho Norte"
        assert result.clients.value == 0
        assert result.clients.available is False
        assert result.active_matters.available is False
        assert result.pending_tasks.available is False
        assert result.upcoming_tasks == []
        assert result.ai_status == "not_available"
        assert all(action.available is False for action in result.actions)

    asyncio.run(run_test())
