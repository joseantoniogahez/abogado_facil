import asyncio

from app.features.matters.repository import MattersRepository
from utils.testing_support.database import MockDatabase


def test_repository_scopes_lists_and_counts(mock_database: MockDatabase) -> None:
    async def run() -> None:
        async with mock_database.Session() as session:
            repository = MattersRepository(session)
            matter = await repository.create(
                firm_id=1, client_id=1, title="Civil", matter_type="Civil", status="active"
            )
            await session.commit()
            assert await repository.get_for_firm(matter_id=matter.id, firm_id=2) is None
            assert len(await repository.list_for_firm(firm_id=1, client_id=1, limit=10, offset=0)) == 1
            assert await repository.count_for_firm(firm_id=1, status="active") == 1

    asyncio.run(run())
