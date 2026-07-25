import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.errors.services import InvalidInputError, NotFoundError
from app.core.security.service.encryption import AesGcmSecretEncryption
from app.features.ai_execution.service import AiProviderFactory


def run(coro):
    return asyncio.run(coro)


def test_build_requires_scoped_credential_before_constructing_provider() -> None:
    credentials = Mock()
    credentials.get_secret = AsyncMock(return_value="test-api-key")
    constructor = Mock(return_value=object())
    factory = AiProviderFactory(credentials, {"openai": constructor})

    result = run(factory.build(user_id=7, firm_id=3, provider="openai", model="gpt-test"))

    assert result is constructor.return_value
    credentials.get_secret.assert_awaited_once_with(user_id=7, firm_id=3, provider="openai")
    constructor.assert_called_once_with(api_key="test-api-key", model="gpt-test")  # pragma: allowlist secret


@pytest.mark.parametrize(
    "failure, message", [(NotFoundError("not found"), "not configured"), (ValueError("invalid"), "invalid")]
)
def test_build_rejects_invalid_credential_without_provider_call(failure, message: str) -> None:
    credentials = Mock()
    credentials.get_secret = AsyncMock(side_effect=failure)
    constructor = Mock()
    factory = AiProviderFactory(credentials, {"openai": constructor})

    with pytest.raises(InvalidInputError, match=message):
        run(factory.build(user_id=7, firm_id=3, provider="openai", model="gpt-test"))
    constructor.assert_not_called()


def test_build_rejects_empty_credential_without_provider_call() -> None:
    credentials = Mock()
    credentials.get_secret = AsyncMock(return_value="   ")
    constructor = Mock()
    factory = AiProviderFactory(credentials, {"openai": constructor})

    with pytest.raises(InvalidInputError, match="invalid"):
        run(factory.build(user_id=7, firm_id=3, provider="openai", model="gpt-test"))
    constructor.assert_not_called()


def test_build_rejects_tampered_aes_gcm_credential_without_provider_call() -> None:
    encryption = AesGcmSecretEncryption(b"x" * 32)
    ciphertext, nonce = encryption.encrypt("test-api-key")
    tampered_prefix = "A" if ciphertext[0] != "A" else "B"
    tampered_ciphertext = f"{tampered_prefix}{ciphertext[1:]}"

    class TamperedCredentialReader:
        async def get_secret(self, *, user_id: int, firm_id: int, provider: str) -> str:
            return encryption.decrypt(tampered_ciphertext, nonce)

    constructor = Mock()
    factory = AiProviderFactory(TamperedCredentialReader(), {"openai": constructor})

    with pytest.raises(InvalidInputError, match="invalid"):
        run(factory.build(user_id=7, firm_id=3, provider="openai", model="gpt-test"))
    constructor.assert_not_called()


def test_build_rejects_unsupported_provider_without_reading_credentials() -> None:
    credentials = Mock()
    credentials.get_secret = AsyncMock()
    factory = AiProviderFactory(credentials)

    with pytest.raises(InvalidInputError, match="Unsupported"):
        run(factory.build(user_id=7, firm_id=3, provider="mock", model="mock-model"))
    credentials.get_secret.assert_not_awaited()
