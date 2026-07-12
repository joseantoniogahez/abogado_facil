import asyncio

from app.features.clients.repository import ClientsRepository
from utils.testing_support.database import MockDatabase


def test_repository_search_count_and_firm_scope(mock_database: MockDatabase) -> None:
    async def run() -> None:
        async with mock_database.Session() as session:
            repository = ClientsRepository(session)
            first = await repository.create(firm_id=1, full_name="Ana Torres", phone="5512341000")
            await repository.create(firm_id=3, full_name="Ana Rivera", phone="5512342000")
            await session.commit()
            assert await repository.count_for_firm(firm_id=1) == 1
            assert len(await repository.list_for_firm(firm_id=1, search="+52 55 1234 1000", limit=10, offset=0)) == 1
            assert await repository.get_for_firm(client_id=first.id, firm_id=3) is None

    asyncio.run(run())
