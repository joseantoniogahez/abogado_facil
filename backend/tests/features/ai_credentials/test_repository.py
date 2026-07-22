import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.features.ai_credentials.repository import AiCredentialsRepository


def _session(result):
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


def test_repository_reads_and_scopes_credentials() -> None:
    async def run() -> None:
        item = SimpleNamespace(provider="openai")
        result = MagicMock()
        result.scalar_one_or_none.return_value = item
        result.scalars.return_value.all.return_value = [item]
        session = _session(result)
        repository = AiCredentialsRepository(session)
        assert await repository.get_for_user(user_id=1, firm_id=2, provider="openai") is item
        assert await repository.list_for_user(user_id=1, firm_id=2) == [item]
        assert session.execute.await_count == 2

    asyncio.run(run())


def test_repository_creates_updates_and_deletes() -> None:
    async def run() -> None:
        result = MagicMock()
        result.rowcount = 1
        session = _session(result)
        repository = AiCredentialsRepository(session)
        created = await repository.create(user_id=1, firm_id=2, provider="openai", encrypted_api_key="x", nonce="n")
        updated = await repository.update(created, encrypted_api_key="y", nonce="m")
        assert updated.encrypted_api_key == "y"
        assert updated.nonce == "m"
        assert await repository.delete(user_id=1, firm_id=2, provider="openai") is True
        session.add.assert_called_once_with(created)
        assert session.flush.await_count == 2
        assert session.refresh.await_count == 2

    asyncio.run(run())
