import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from cryptography.exceptions import InvalidTag

from app.core.errors.services import InvalidInputError, NotFoundError
from app.core.security.service.encryption import AesGcmSecretEncryption
from app.features.ai_credentials.service import AiCredentialsService


class Uow:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def item(provider="openai"):
    return SimpleNamespace(
        provider=provider,
        encrypted_api_key="encrypted",  # pragma: allowlist secret
        nonce="nonce",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def service(repository):
    return AiCredentialsService(repository, Uow(), AesGcmSecretEncryption(b"x" * 32))


def test_list_save_replace_get_and_delete() -> None:
    asyncio.run(_test_list_save_replace_get_and_delete())


async def _test_list_save_replace_get_and_delete() -> None:
    repository = AsyncMock()
    repository.list_for_user.return_value = [item()]
    repository.get_for_user.side_effect = [None, item(), None]
    created = item()
    repository.create.return_value = created
    repository.update.return_value = created
    repository.delete.return_value = True
    target = service(repository)

    assert (await target.list(user_id=1, firm_id=2)).items[0].provider == "openai"
    assert (await target.save(user_id=1, firm_id=2, provider="openai", api_key="sk-test-secret")).configured
    assert (await target.save(user_id=1, firm_id=2, provider="openai", api_key="sk-test-secret")).provider == "openai"
    repository.get_for_user.return_value = None
    with pytest.raises(NotFoundError):
        await target.get_secret(user_id=1, firm_id=2, provider="gemini")
    stored = item()
    stored.encrypted_api_key, stored.nonce = target.encryption.encrypt("secret")
    repository.get_for_user.side_effect = None
    repository.get_for_user.return_value = stored
    assert await target.get_secret(user_id=1, firm_id=2, provider="openai") == "secret"
    await target.delete(user_id=1, firm_id=2, provider="openai")


def test_invalid_and_missing_provider_paths() -> None:
    asyncio.run(_test_invalid_and_missing_provider_paths())


async def _test_invalid_and_missing_provider_paths() -> None:
    repository = AsyncMock()
    repository.delete.return_value = False
    repository.get_for_user.return_value = None
    target = service(repository)

    with pytest.raises(InvalidInputError):
        await target.save(user_id=1, firm_id=2, provider="other", api_key="sk-test-secret")
    with pytest.raises(InvalidInputError):
        await target.delete(user_id=1, firm_id=2, provider="other")
    with pytest.raises(NotFoundError):
        await target.delete(user_id=1, firm_id=2, provider="openai")


def test_aes_gcm_rejects_bad_key_and_detects_tampering() -> None:
    with pytest.raises(ValueError):
        AesGcmSecretEncryption(b"short")
    adapter = AesGcmSecretEncryption(b"x" * 32)
    ciphertext, nonce = adapter.encrypt("secret")
    assert adapter.decrypt(ciphertext, nonce) == "secret"
    with pytest.raises(InvalidTag):
        adapter.decrypt(ciphertext[:-2] + "aa", nonce)
