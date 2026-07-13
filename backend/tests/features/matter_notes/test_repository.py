import asyncio

from app.features.matter_notes.repository import MatterNotesRepository
from utils.testing_support.database import MockDatabase


def test_repository_scopes_and_orders_notes(mock_database: MockDatabase) -> None:
    async def run() -> None:
        async with mock_database.Session() as session:
            repository = MatterNotesRepository(session)
            first = await repository.create(firm_id=1, matter_id=1, content="Primera", is_relevant=False)
            second = await repository.create(firm_id=1, matter_id=1, content="Segunda", is_relevant=True)
            await session.commit()
            assert [note.id for note in await repository.list_for_matter(firm_id=1, matter_id=1)] == [
                second.id,
                first.id,
            ]
            assert await repository.get_for_matter(note_id=first.id, matter_id=1, firm_id=2) is None
            assert await repository.count_for_matter(firm_id=1, matter_id=1) == 2

    asyncio.run(run())
