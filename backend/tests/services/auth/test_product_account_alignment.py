import asyncio
from unittest.mock import AsyncMock

from app.core.common.records import FirmRecord, UserRecord
from app.features.auth.schemas import LoginCommand, RegisterUserCommand
from utils.testing_support.auth_service import assert_unit_of_work_scope_committed, build_service


def test_registration_creates_firm_owner_and_normalizes_email_atomically() -> None:
    service, repository = build_service()
    repository.get_firm = AsyncMock(return_value=FirmRecord(id=41, name="Lic. Maria"))
    repository.create_firm = AsyncMock(return_value=FirmRecord(id=41, name="Lic. Maria"))
    repository.assign_role_by_name = AsyncMock(return_value=None)
    repository.email_exists = AsyncMock(return_value=False)
    repository.create_user = AsyncMock(
        return_value=UserRecord(
            id=7,
            email="maria@example.com",
            first_name="Maria",
            middle_name=None,
            last_name="Perez",
            display_name="Lic. Maria",
            hashed_password="hash",  # pragma: allowlist secret
            disabled=False,
            firm_id=41,
        )
    )
    repository.get_user_effective_permission_ids = AsyncMock(return_value=())

    result = asyncio.run(
        service.register(
            RegisterUserCommand(
                first_name="  Maria ",
                middle_name=None,
                last_name=" Perez ",
                display_name=" Lic. Maria ",
                email=" MARIA@EXAMPLE.COM ",
                password="SecurePass9",  # pragma: allowlist secret
            )
        )
    )

    assert (
        result.email,
        result.first_name,
        result.middle_name,
        result.last_name,
        result.display_name,
        result.firm_name,
    ) == (
        "maria@example.com",
        "Maria",
        None,
        "Perez",
        "Lic. Maria",
        "Lic. Maria",
    )
    repository.create_firm.assert_awaited_once_with(name="Lic. Maria")
    repository.assign_role_by_name.assert_awaited_once_with(user_id=7, role_name="account_owner")
    assert_unit_of_work_scope_committed(service.unit_of_work)


def test_login_uses_normalized_email_as_jwt_subject() -> None:
    service, repository = build_service()
    password_hash = service.password_service.hash_password("SecurePass9")
    repository.get_by_email = AsyncMock(
        return_value=UserRecord(
            id=7,
            email="maria@example.com",
            first_name="Maria",
            middle_name=None,
            last_name="Perez",
            display_name="Maria Perez",
            hashed_password=password_hash,
            disabled=False,
            firm_id=41,
        )
    )
    repository.get_rbac_version = AsyncMock(return_value="a" * 64)

    result = asyncio.run(service.login(LoginCommand(email=" MARIA@EXAMPLE.COM ", password="SecurePass9")))
    payload = service.token_service.decode_access_token(result.access_token)

    assert payload is not None
    assert payload.sub == "maria@example.com"
