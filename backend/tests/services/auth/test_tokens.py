import asyncio
from unittest.mock import patch

import pytest

from app.core.errors.services import UnauthorizedError
from app.features.auth.principal import CurrentPrincipal
from app.features.auth.schemas import AccessTokenPayload
from utils.testing_support.auth_service import build_service, build_user


def build_access_token_payload(*, rbac_version: str = "0" * 64) -> AccessTokenPayload:
    return AccessTokenPayload(
        sub="john@example.com",
        iss="unit-test-issuer",
        aud="unit-test-audience",
        iat=123456700,
        exp=123456789,
        jti="token-123",
        rbac_version=rbac_version,
    )


def test_get_user_from_token_raises_for_invalid_payload() -> None:
    service, repository = build_service()

    async def run_test() -> None:
        with (
            patch.object(service.token_service, "decode_access_token", return_value=None),
            pytest.raises(UnauthorizedError) as exc_info,
        ):
            await service.get_user_from_token("bad-token")

        assert "Could not validate credentials" in str(exc_info.value)
        repository.get_by_email.assert_not_awaited()

    asyncio.run(run_test())


def test_get_user_from_token_raises_when_user_does_not_exist() -> None:
    service, repository = build_service()
    payload = build_access_token_payload()
    repository.get_by_email.return_value = None

    async def run_test() -> None:
        with (
            patch.object(service.token_service, "decode_access_token", return_value=payload),
            pytest.raises(UnauthorizedError),
        ):
            await service.get_user_from_token("valid-token")

        repository.get_by_email.assert_awaited_once_with("john@example.com")

    asyncio.run(run_test())


def test_get_user_from_token_returns_principal_when_token_is_valid() -> None:
    service, repository = build_service()
    payload = build_access_token_payload()
    expected_user = build_user(service, firm_id=17)
    repository.get_by_email.return_value = expected_user

    async def run_test() -> None:
        with patch.object(service.token_service, "decode_access_token", return_value=payload):
            user = await service.get_user_from_token("valid-token")

        assert isinstance(user, CurrentPrincipal)
        assert user.id == expected_user.id
        assert user.email == expected_user.email
        assert user.first_name == expected_user.first_name
        assert user.last_name == expected_user.last_name
        assert user.display_name == expected_user.display_name
        assert user.disabled == expected_user.disabled
        assert user.firm_id == expected_user.firm_id
        repository.get_by_email.assert_awaited_once_with("john@example.com")
        repository.get_rbac_version.assert_awaited_once_with(1)

    asyncio.run(run_test())


def test_get_user_from_token_raises_when_rbac_version_changed() -> None:
    service, repository = build_service()
    payload = build_access_token_payload(rbac_version="1" * 64)
    expected_user = build_user(service)
    repository.get_by_email.return_value = expected_user

    async def run_test() -> None:
        with (
            patch.object(service.token_service, "decode_access_token", return_value=payload),
            pytest.raises(UnauthorizedError) as exc_info,
        ):
            await service.get_user_from_token("valid-token")

        assert "Could not validate credentials" in str(exc_info.value)
        repository.get_by_email.assert_awaited_once_with("john@example.com")
        repository.get_rbac_version.assert_awaited_once_with(1)

    asyncio.run(run_test())
