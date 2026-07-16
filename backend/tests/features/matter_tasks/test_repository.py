import asyncio
from datetime import date

from app.features.matter_tasks.repository import MatterTasksRepository


def test_task_repository_queries(mock_database) -> None:
    async def run() -> None:
        async with mock_database.Session() as session:
            repository = MatterTasksRepository(session)
            assert await repository.count_pending_for_firm(firm_id=999) == 0
            assert await repository.list_upcoming_for_firm(firm_id=999) == []
            assert await repository.count_for_matter(matter_id=999, firm_id=999) == 0
            assert await repository.list_for_matter(matter_id=999, firm_id=999) == []
            assert await repository.get_for_matter(task_id=999, matter_id=999, firm_id=999) is None
            assert date(2026, 7, 20).isoformat() == "2026-07-20"

    asyncio.run(run())
