import asyncio
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.errors.repositories import RepositoryConflictError, RepositoryInternalError
from app.features.auth.models import User
from app.features.auth.repository import AuthRepository
from utils.testing_support.repositories import build_session_mock


def test_auth_repository_user_has_permission_delegates_to_scope_lookup() -> None:
    session = build_session_mock()
    repository = AuthRepository(session=session)

    async def run_test() -> None:
        get_scope_mock = AsyncMock(return_value="any")
        with patch.object(repository, "get_user_permission_scope", get_scope_mock):
            has_permission = await repository.user_has_permission(user_id=3, permission_id="roles:manage")

        assert has_permission is True
        get_scope_mock.assert_awaited_once_with(
            user_id=3,
            permission_id="roles:manage",
        )

    asyncio.run(run_test())


def test_auth_repository_get_rbac_version_returns_stable_digest_for_effective_permissions() -> None:
    session = build_session_mock()
    repository = AuthRepository(session=session)
    result = MagicMock()
    result.all.return_value = [
        ("role_permissions:manage", "own"),
        ("role_permissions:manage", "any"),
        ("roles:manage", "tenant"),
        ("ignored", "invalid"),
    ]
    session.execute.return_value = result

    async def run_test() -> None:
        rbac_version = await repository.get_rbac_version(user_id=7)

        expected = hashlib.sha256(b"role_permissions:manage:any|roles:manage:tenant").hexdigest()
        assert rbac_version == expected
        session.execute.assert_awaited_once()

    asyncio.run(run_test())


def test_auth_repository_get_user_effective_permission_ids_returns_sorted_unique_ids() -> None:
    session = build_session_mock()
    repository = AuthRepository(session=session)
    result = MagicMock()
    scalars_result = MagicMock()
    scalars_result.all.return_value = [
        "users:manage",
        "roles:manage",
        "users:manage",
        "role_permissions:manage",
    ]
    result.scalars.return_value = scalars_result
    session.execute.return_value = result

    async def run_test() -> None:
        permission_ids = await repository.get_user_effective_permission_ids(user_id=7)

        assert permission_ids == (
            "role_permissions:manage",
            "roles:manage",
            "users:manage",
        )
        session.execute.assert_awaited_once()

    asyncio.run(run_test())


def test_auth_repository_create_user_translates_integrity_error_to_repository_conflict() -> None:
    session = build_session_mock()
    session.flush.side_effect = IntegrityError("insert", {}, Exception("duplicate"))
    repository = AuthRepository(session=session)

    async def run_test() -> None:
        with pytest.raises(RepositoryConflictError) as exc_info:
            await repository.create_user(
                email="john@example.com",
                first_name="John",
                middle_name=None,
                last_name="Doe",
                display_name="John Doe",
                hashed_password="hash",  # pragma: allowlist secret
                disabled=False,
            )

        assert "Email already exists" in str(exc_info.value)
        assert exc_info.value.details == {"email": "john@example.com"}
        session.refresh.assert_not_awaited()

    asyncio.run(run_test())


def test_auth_repository_get_firm_returns_none_when_not_found() -> None:
    session = build_session_mock()
    session.get.return_value = None
    repository = AuthRepository(session=session)

    assert asyncio.run(repository.get_firm(404)) is None
    session.get.assert_awaited_once()


def test_auth_repository_update_firm_raises_when_not_found() -> None:
    session = build_session_mock()
    session.get.return_value = None
    repository = AuthRepository(session=session)

    with pytest.raises(RepositoryInternalError, match="Firm 404 not found"):
        asyncio.run(repository.update_firm(404, name="Missing Firm"))


def test_auth_repository_create_user_translates_non_email_integrity_error_to_repository_internal_error() -> None:
    session = build_session_mock()
    session.flush.side_effect = IntegrityError("insert", {}, Exception("constraint"))
    repository = AuthRepository(session=session)

    async def run_test() -> None:
        with pytest.raises(RepositoryInternalError) as exc_info:
            await repository.create_user(
                email=None,
                first_name="John",
                middle_name=None,
                last_name="Doe",
                display_name="John Doe",
                hashed_password="hash",  # pragma: allowlist secret
                disabled=False,
            )

        assert "Internal server error" in str(exc_info.value)
        session.refresh.assert_not_awaited()

    asyncio.run(run_test())


def test_auth_repository_update_user_translates_email_integrity_error_to_repository_conflict() -> None:
    session = build_session_mock()
    session.flush.side_effect = IntegrityError("update", {}, Exception("duplicate"))
    user = User(
        id=3,
        email="john@example.com",
        first_name="John",
        middle_name=None,
        last_name="Doe",
        display_name="John Doe",
        hashed_password="hash",  # pragma: allowlist secret
        disabled=False,
    )
    session.get.return_value = user
    session.merge.return_value = user
    repository = AuthRepository(session=session)

    async def run_test() -> None:
        with pytest.raises(RepositoryConflictError) as exc_info:
            await repository.update_user(3, email="new-user@example.com")

        assert "Email already exists" in str(exc_info.value)
        assert exc_info.value.details == {"email": "new-user@example.com"}
        session.refresh.assert_not_awaited()

    asyncio.run(run_test())


def test_auth_repository_update_user_translates_other_integrity_errors_to_repository_internal_error() -> None:
    session = build_session_mock()
    session.flush.side_effect = IntegrityError("update", {}, Exception("constraint"))
    user = User(
        id=3,
        email="john@example.com",
        first_name="John",
        middle_name=None,
        last_name="Doe",
        display_name="John Doe",
        hashed_password="hash",  # pragma: allowlist secret
        disabled=False,
    )
    session.get.return_value = user
    session.merge.return_value = user
    repository = AuthRepository(session=session)

    async def run_test() -> None:
        with pytest.raises(RepositoryInternalError) as exc_info:
            await repository.update_user(3, hashed_password="new-hash")  # pragma: allowlist secret

        assert "Internal server error" in str(exc_info.value)
        session.refresh.assert_not_awaited()

    asyncio.run(run_test())


def test_auth_repository_update_user_raises_internal_error_when_user_does_not_exist() -> None:
    session = build_session_mock()
    session.get.return_value = None
    repository = AuthRepository(session=session)

    async def run_test() -> None:
        with pytest.raises(RepositoryInternalError) as exc_info:
            await repository.update_user(404, email="new-user@example.com")

        assert "User 404 not found" in str(exc_info.value)
        session.merge.assert_not_awaited()
        session.flush.assert_not_awaited()

    asyncio.run(run_test())
