import asyncio
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest

from app.core.common.records import FirmRecord, UserRecord
from app.core.errors.repositories import RepositoryConflictError
from app.core.errors.services import ConflictError, ForbiddenError, InvalidInputError, UnauthorizedError
from app.features.auth.schemas import LoginCommand, RegisterUserCommand
from utils.testing_support.auth_service import (
    assert_unit_of_work_scope_committed,
    build_service,
    build_user,
)


def _build_registration(*, email: str = " John@Example.COM ") -> RegisterUserCommand:
    return RegisterUserCommand(
        first_name=" John ",
        middle_name=" Paul ",
        last_name=" Doe ",
        display_name=" John Doe ",
        email=email,
        firm_name=" Doe Legal ",
        password="StrongPass1",  # pragma: allowlist secret
    )


async def _create_user_record(**kwargs: Any) -> UserRecord:
    return UserRecord(
        id=42,
        email=cast(str, kwargs["email"]),
        first_name=cast(str, kwargs["first_name"]),
        middle_name=cast(str | None, kwargs["middle_name"]),
        last_name=cast(str, kwargs["last_name"]),
        display_name=cast(str, kwargs["display_name"]),
        hashed_password=cast(str, kwargs["hashed_password"]),
        disabled=cast(bool, kwargs["disabled"]),
        firm_id=cast(int, kwargs["firm_id"]),
    )


def _configure_registration_persistence(repository: Any) -> None:
    firm = FirmRecord(id=9, name="Doe Legal")
    repository.create_firm.return_value = firm
    repository.get_firm.return_value = firm
    repository.create_user.side_effect = _create_user_record


def test_authenticate_or_raise_raises_unauthorized_when_user_not_found() -> None:
    service, repository = build_service()
    credentials = LoginCommand(email=" John@Example.COM ", password="StrongPass1")
    repository.get_by_email.return_value = None

    async def run_test() -> None:
        with pytest.raises(UnauthorizedError) as exc_info:
            await service._authenticate_or_raise(credentials)

        assert "Invalid email or password" in str(exc_info.value)
        repository.get_by_email.assert_awaited_once_with("john@example.com")

    asyncio.run(run_test())


def test_authenticate_or_raise_raises_unauthorized_when_password_is_invalid() -> None:
    service, repository = build_service()
    credentials = LoginCommand(email="john@example.com", password="WrongPass1")
    repository.get_by_email.return_value = build_user(service, password="StrongPass1")

    async def run_test() -> None:
        with pytest.raises(UnauthorizedError):
            await service._authenticate_or_raise(credentials)

    asyncio.run(run_test())


def test_authenticate_or_raise_raises_forbidden_for_disabled_user() -> None:
    service, repository = build_service()
    credentials = LoginCommand(email="john@example.com", password="StrongPass1")
    repository.get_by_email.return_value = build_user(service, disabled=True)

    async def run_test() -> None:
        with pytest.raises(ForbiddenError) as exc_info:
            await service._authenticate_or_raise(credentials)

        assert "Inactive user" in str(exc_info.value)

    asyncio.run(run_test())


def test_login_returns_bearer_token_for_authenticated_user() -> None:
    service, repository = build_service()
    credentials = LoginCommand(email="john@example.com", password="StrongPass1")
    repository.get_by_email.return_value = build_user(service)

    async def run_test() -> None:
        with patch.object(
            service.token_service,
            "encode_access_token",
            return_value="encoded-token",
        ) as encode_access_token:
            token = await service.login(credentials)

        assert token.access_token == "encoded-token"
        assert token.token_type == "bearer"
        repository.get_rbac_version.assert_awaited_once_with(1)
        encode_access_token.assert_called_once_with(
            subject="john@example.com",
            rbac_version="0" * 64,
        )

    asyncio.run(run_test())


def test_register_raises_conflict_when_email_already_exists() -> None:
    service, repository = build_service()
    repository.email_exists.return_value = True
    registration = _build_registration()

    async def run_test() -> None:
        with pytest.raises(ConflictError) as exc_info:
            await service.register(registration)

        assert "Email already exists" in str(exc_info.value)
        assert exc_info.value.details == {"email": "john@example.com"}
        repository.create_firm.assert_not_awaited()
        repository.create_user.assert_not_awaited()

    asyncio.run(run_test())


def test_register_maps_invalid_required_name_to_invalid_input() -> None:
    service, repository = build_service()
    registration = _build_registration().model_copy(update={"display_name": "   "})

    async def run_test() -> None:
        with pytest.raises(InvalidInputError, match="Display name is required"):
            await service.register(registration)

        repository.email_exists.assert_not_awaited()

    asyncio.run(run_test())


def test_register_creates_user_and_returns_authenticated_user() -> None:
    service, repository = build_service()
    registration = _build_registration()
    _configure_registration_persistence(repository)

    async def run_test() -> None:
        authenticated_user = await service.register(registration)

        assert authenticated_user.id == 42
        assert authenticated_user.email == "john@example.com"
        assert authenticated_user.first_name == "John"
        assert authenticated_user.middle_name == "Paul"
        assert authenticated_user.last_name == "Doe"
        assert authenticated_user.display_name == "John Doe"
        assert authenticated_user.firm_name == "Doe Legal"
        assert authenticated_user.disabled is False
        assert authenticated_user.permissions == ()
        repository.email_exists.assert_awaited_once_with("john@example.com")
        repository.create_firm.assert_awaited_once_with(name="Doe Legal")
        repository.create_user.assert_awaited_once()
        repository.assign_role_by_name.assert_awaited_once_with(
            user_id=42,
            role_name="account_owner",
        )
        assert_unit_of_work_scope_committed(service.unit_of_work)
        created_kwargs = repository.create_user.await_args.kwargs
        assert created_kwargs["email"] == "john@example.com"
        assert created_kwargs["first_name"] == "John"
        assert created_kwargs["middle_name"] == "Paul"
        assert created_kwargs["last_name"] == "Doe"
        assert created_kwargs["display_name"] == "John Doe"
        assert created_kwargs["firm_id"] == 9
        assert created_kwargs["disabled"] is False
        assert created_kwargs["hashed_password"] != registration.password
        assert (
            service.password_service.verify_password(
                registration.password,
                created_kwargs["hashed_password"],
            )
            is True
        )

    asyncio.run(run_test())


def test_register_maps_effective_permissions_into_authenticated_user_result() -> None:
    service, repository = build_service()
    repository.get_user_effective_permission_ids = AsyncMock(
        return_value=("users:manage", "roles:manage", "users:manage")
    )
    registration = _build_registration(email="john@example.com")
    _configure_registration_persistence(repository)

    async def run_test() -> None:
        authenticated_user = await service.register(registration)

        assert authenticated_user.permissions == ("roles:manage", "users:manage")
        repository.get_user_effective_permission_ids.assert_awaited_once_with(42)

    asyncio.run(run_test())


def test_register_propagates_repository_conflict_from_create() -> None:
    service, repository = build_service()
    registration = _build_registration(email="john@example.com")
    repository.create_firm.return_value = FirmRecord(id=9, name="Doe Legal")
    repository.create_user.side_effect = RepositoryConflictError(
        message="Email already exists",
        details={"email": "john@example.com"},
    )

    async def run_test() -> None:
        with pytest.raises(RepositoryConflictError) as exc_info:
            await service.register(registration)

        assert "Email already exists" in str(exc_info.value)
        assert exc_info.value.details == {"email": "john@example.com"}

    asyncio.run(run_test())
