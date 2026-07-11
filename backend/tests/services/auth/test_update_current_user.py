import asyncio
from unittest.mock import AsyncMock

import pytest

from app.core.common.records import FirmRecord, UserRecord
from app.core.errors.repositories import RepositoryConflictError, RepositoryInternalError
from app.core.errors.services import ConflictError, InvalidInputError, UnauthorizedError
from app.features.auth.principal import CurrentPrincipal
from app.features.auth.schemas import UpdateCurrentUserCommand
from app.features.auth.service import AuthService
from utils.testing_support.auth_service import assert_unit_of_work_scope_committed, build_service


def _build_user(
    service: AuthService,
    *,
    user_id: int = 1,
    email: str = "maria@example.com",
    password: str = "StrongPass1",
    firm_id: int | None = 41,
) -> UserRecord:
    return UserRecord(
        id=user_id,
        email=email,
        first_name="Maria",
        middle_name=None,
        last_name="Perez",
        display_name="Maria Perez",
        hashed_password=service.password_service.hash_password(password),
        disabled=False,
        firm_id=firm_id,
    )


def test_validate_update_request_enforces_required_combinations() -> None:
    service, _ = build_service()

    with pytest.raises(InvalidInputError, match="new_password is required"):
        service._validate_update_request(
            UpdateCurrentUserCommand(current_password="CurrentPass1")  # pragma: allowlist secret
        )

    with pytest.raises(InvalidInputError, match="current_password is required"):
        service._validate_update_request(
            UpdateCurrentUserCommand(new_password="NewPass123")  # pragma: allowlist secret
        )

    with pytest.raises(InvalidInputError, match="At least one field must be provided"):
        service._validate_update_request(UpdateCurrentUserCommand())


def test_build_email_change_handles_absent_unchanged_and_available_email() -> None:
    service, repository = build_service()
    current_user = _build_user(service, user_id=7)
    updates = service._profile_updates

    async def run_test() -> None:
        assert await updates._build_email_change(current_user, None) == ("maria@example.com", {})
        assert await updates._build_email_change(current_user, " MARIA@EXAMPLE.COM ") == (
            "maria@example.com",
            {},
        )
        assert await updates._build_email_change(current_user, " NEW@EXAMPLE.COM ") == (
            "new@example.com",
            {"email": "new@example.com"},
        )
        repository.email_exists.assert_awaited_once_with("new@example.com", exclude_user_id=7)

    asyncio.run(run_test())


def test_build_email_change_rejects_taken_email() -> None:
    service, repository = build_service()
    current_user = _build_user(service, user_id=8)
    repository.email_exists.return_value = True

    async def run_test() -> None:
        with pytest.raises(ConflictError) as exc_info:
            await service._profile_updates._build_email_change(current_user, "taken@example.com")

        assert exc_info.value.details == {"email": "taken@example.com"}
        repository.email_exists.assert_awaited_once_with("taken@example.com", exclude_user_id=8)

    asyncio.run(run_test())


def test_build_password_change_validates_current_and_new_password() -> None:
    service, _ = build_service()
    current_user = _build_user(service, password="StrongPass1")
    updates = service._profile_updates

    assert (
        updates._build_password_change(
            current_user, UpdateCurrentUserCommand(email=current_user.email), current_user.email
        )
        == {}
    )

    with pytest.raises(UnauthorizedError, match="Current password is invalid"):
        updates._build_password_change(
            current_user,
            UpdateCurrentUserCommand(new_password="AnotherPass1"),  # pragma: allowlist secret
            current_user.email,
        )

    with pytest.raises(UnauthorizedError, match="Current password is invalid"):
        updates._build_password_change(
            current_user,
            UpdateCurrentUserCommand(
                current_password="WrongPass1",  # pragma: allowlist secret
                new_password="AnotherPass1",  # pragma: allowlist secret
            ),
            current_user.email,
        )

    with pytest.raises(InvalidInputError, match="New password must be different"):
        updates._build_password_change(
            current_user,
            UpdateCurrentUserCommand(
                current_password="StrongPass1",  # pragma: allowlist secret
                new_password="StrongPass1",  # pragma: allowlist secret
            ),
            current_user.email,
        )

    changes = updates._build_password_change(
        current_user,
        UpdateCurrentUserCommand(
            current_password="StrongPass1",  # pragma: allowlist secret
            new_password="AnotherPass1",  # pragma: allowlist secret
        ),
        current_user.email,
    )
    hashed_password = changes["hashed_password"]
    assert hashed_password is not None
    assert service.password_service.verify_password("AnotherPass1", hashed_password) is True


def test_update_current_user_persists_all_profile_changes() -> None:
    service, repository = build_service()
    current_user = _build_user(service, user_id=9, password="StrongPass1")
    updated_user = current_user.model_copy(
        update={
            "email": "new@example.com",
            "first_name": "Mariana",
            "middle_name": "Elena",
            "last_name": "Robles",
            "display_name": "Lic. Mariana",
        }
    )
    repository.get_by_email.return_value = current_user
    repository.update_user.return_value = updated_user
    repository.get_firm.return_value = FirmRecord(id=41, name="Robles Legal")
    update_data = UpdateCurrentUserCommand(
        email=" NEW@EXAMPLE.COM ",
        first_name=" Mariana ",
        middle_name="  Elena ",
        last_name=" Robles ",
        display_name=" Lic. Mariana ",
        firm_name=" Robles Legal ",
        current_password="StrongPass1",  # pragma: allowlist secret
        new_password="AnotherPass1",  # pragma: allowlist secret
    )

    result = asyncio.run(service.update_current_user(CurrentPrincipal.from_domain(current_user), update_data))

    assert (
        result.email,
        result.first_name,
        result.middle_name,
        result.last_name,
        result.display_name,
        result.firm_name,
    ) == (
        "new@example.com",
        "Mariana",
        "Elena",
        "Robles",
        "Lic. Mariana",
        "Robles Legal",
    )
    repository.update_firm.assert_awaited_once_with(41, name="Robles Legal")
    repository.update_user.assert_awaited_once()
    update_kwargs = repository.update_user.await_args.kwargs
    assert update_kwargs | {"hashed_password": None} == {
        "email": "new@example.com",
        "first_name": "Mariana",
        "middle_name": "Elena",
        "last_name": "Robles",
        "display_name": "Lic. Mariana",
        "hashed_password": None,
    }
    assert service.password_service.verify_password("AnotherPass1", update_kwargs["hashed_password"]) is True
    assert_unit_of_work_scope_committed(service.unit_of_work)


def test_update_current_user_normalizes_empty_middle_name_to_none() -> None:
    service, repository = build_service()
    current_user = _build_user(service)
    current_user = current_user.model_copy(update={"middle_name": "Elena"})
    repository.get_by_email.return_value = current_user
    repository.update_user.return_value = current_user.model_copy(update={"middle_name": None})
    repository.get_firm.return_value = FirmRecord(id=41, name="Maria Perez")

    result = asyncio.run(
        service.update_current_user(
            CurrentPrincipal.from_domain(current_user),
            UpdateCurrentUserCommand(middle_name="   "),
        )
    )

    assert result.middle_name is None
    repository.update_user.assert_awaited_once_with(current_user.id, middle_name=None)


def test_update_current_user_updates_only_firm_without_rewriting_user() -> None:
    service, repository = build_service()
    current_user = _build_user(service)
    repository.get_by_email.return_value = current_user
    repository.get_firm.return_value = FirmRecord(id=41, name="Nuevo Despacho")

    result = asyncio.run(
        service.update_current_user(
            CurrentPrincipal.from_domain(current_user),
            UpdateCurrentUserCommand(firm_name=" Nuevo Despacho "),
        )
    )

    assert result.firm_name == "Nuevo Despacho"
    repository.update_firm.assert_awaited_once_with(41, name="Nuevo Despacho")
    repository.update_user.assert_not_awaited()


def test_update_current_user_rejects_firm_change_without_firm() -> None:
    service, repository = build_service()
    current_user = _build_user(service, firm_id=None)
    repository.get_by_email.return_value = current_user

    with pytest.raises(InvalidInputError, match="User does not belong to a firm"):
        asyncio.run(
            service.update_current_user(
                CurrentPrincipal.from_domain(current_user),
                UpdateCurrentUserCommand(firm_name="Nuevo Despacho"),
            )
        )


def test_update_current_user_raises_when_no_changes_are_detected() -> None:
    service, repository = build_service()
    current_user = _build_user(service)
    repository.get_by_email.return_value = current_user

    with pytest.raises(InvalidInputError, match="No changes detected"):
        asyncio.run(
            service.update_current_user(
                CurrentPrincipal.from_domain(current_user),
                UpdateCurrentUserCommand(display_name="  Maria Perez "),
            )
        )

    repository.update_user.assert_not_awaited()


@pytest.mark.parametrize(
    "repository_error",
    [
        RepositoryConflictError(message="Email already exists", details={"email": "new@example.com"}),
        RepositoryInternalError(),
    ],
)
def test_update_current_user_propagates_repository_errors(repository_error: Exception) -> None:
    service, repository = build_service()
    current_user = _build_user(service)
    repository.get_by_email.return_value = current_user
    repository.update_user.side_effect = repository_error

    with pytest.raises(type(repository_error)):
        asyncio.run(
            service.update_current_user(
                CurrentPrincipal.from_domain(current_user),
                UpdateCurrentUserCommand(display_name="Lic. Maria"),
            )
        )


def test_get_authenticated_user_maps_effective_permissions() -> None:
    service, repository = build_service()
    current_user = _build_user(service, user_id=9)
    repository.get_user_effective_permission_ids = AsyncMock(
        return_value=("users:manage", "roles:manage", "users:manage")
    )

    authenticated_user = asyncio.run(service.get_authenticated_user(CurrentPrincipal.from_domain(current_user)))

    assert authenticated_user.email == "maria@example.com"
    assert authenticated_user.permissions == ("roles:manage", "users:manage")
    repository.get_user_effective_permission_ids.assert_awaited_once_with(9)


def test_get_authenticated_user_returns_empty_permissions_without_rbac_grants() -> None:
    service, repository = build_service()
    current_user = _build_user(service, user_id=10)
    repository.get_user_effective_permission_ids = AsyncMock(return_value=())

    authenticated_user = asyncio.run(service.get_authenticated_user(CurrentPrincipal.from_domain(current_user)))

    assert authenticated_user.permissions == ()
    repository.get_user_effective_permission_ids.assert_awaited_once_with(10)


def test_update_current_user_raises_unauthorized_when_principal_user_is_missing() -> None:
    service, repository = build_service()
    current_user = _build_user(service, user_id=55, email="ghost@example.com")
    repository.get_by_email.return_value = None

    with pytest.raises(UnauthorizedError, match="Could not validate credentials"):
        asyncio.run(
            service.update_current_user(
                CurrentPrincipal.from_domain(current_user),
                UpdateCurrentUserCommand(display_name="Ghost User"),
            )
        )
