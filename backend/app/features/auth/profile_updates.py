from collections.abc import Callable
from typing import Any, Protocol

from app.core.common.records import FirmRecord, UserRecord
from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import ConflictError, InvalidInputError, UnauthorizedError
from app.core.security.policies import normalize_required_name
from app.core.security.service import PasswordServicePort
from app.features.auth.schemas import UpdateCurrentUserCommand

NormalizeEmail = Callable[[str], str]
ValidatePasswordPolicy = Callable[[str, str], None]
UserChanges = dict[str, str | None]


class AuthProfileRepositoryPort(Protocol):
    async def email_exists(self, email: str, *, exclude_user_id: int | None = None) -> bool: ...
    async def update_user(self, user_id: int, **changes: Any) -> UserRecord: ...
    async def update_firm(self, firm_id: int, *, name: str) -> FirmRecord: ...


class AuthProfileUpdates:
    def __init__(
        self,
        *,
        auth_repository: AuthProfileRepositoryPort,
        unit_of_work: UnitOfWorkPort,
        password_service: PasswordServicePort,
        normalize_email: NormalizeEmail,
        validate_password_policy: ValidatePasswordPolicy,
    ):
        self._repository = auth_repository
        self._unit_of_work = unit_of_work
        self._password_service = password_service
        self._normalize_email = normalize_email
        self._validate_password_policy = validate_password_policy

    @staticmethod
    def validate_update_request(data: UpdateCurrentUserCommand) -> None:
        if data.current_password and data.new_password is None:
            raise InvalidInputError(message="new_password is required when current_password is provided")
        if data.new_password and data.current_password is None:
            raise InvalidInputError(message="current_password is required to update password")
        if all(
            value is None
            for value in (
                data.email,
                data.first_name,
                data.middle_name,
                data.last_name,
                data.display_name,
                data.firm_name,
                data.new_password,
            )
        ):
            raise InvalidInputError(message="At least one field must be provided to update the user")

    async def _build_email_change(self, user: UserRecord, requested_email: str | None) -> tuple[str, UserChanges]:
        if requested_email is None:
            return user.email, {}

        email = self._normalize_email(requested_email)
        if email == user.email:
            return email, {}
        if await self._repository.email_exists(email, exclude_user_id=user.id):
            raise ConflictError(message="Email already exists", details={"email": email})
        return email, {"email": email}

    @staticmethod
    def _normalize_profile_field(field: str, value: str) -> str | None:
        if field == "middle_name":
            return " ".join(value.split()) or None
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "display_name": "Display name",
        }
        return normalize_required_name(value, field_name=labels[field])

    @classmethod
    def _build_profile_changes(cls, user: UserRecord, data: UpdateCurrentUserCommand) -> UserChanges:
        changes: UserChanges = {}
        fields = (
            ("first_name", data.first_name, user.first_name),
            ("middle_name", data.middle_name, user.middle_name),
            ("last_name", data.last_name, user.last_name),
            ("display_name", data.display_name, user.display_name),
        )
        for field, requested_value, current_value in fields:
            if requested_value is None:
                continue
            value = cls._normalize_profile_field(field, requested_value)
            if value != current_value:
                changes[field] = value
        return changes

    async def _update_firm(self, user: UserRecord, requested_name: str | None) -> None:
        if requested_name is None:
            return
        if user.firm_id is None:
            raise InvalidInputError(message="User does not belong to a firm")
        await self._repository.update_firm(
            user.firm_id,
            name=normalize_required_name(requested_name, field_name="Firm name"),
        )

    def _build_password_change(
        self,
        user: UserRecord,
        data: UpdateCurrentUserCommand,
        email: str,
    ) -> UserChanges:
        if data.new_password is None:
            return {}
        if data.current_password is None or not self._password_service.verify_password(
            data.current_password, user.hashed_password
        ):
            raise UnauthorizedError(message="Current password is invalid")
        if self._password_service.verify_password(data.new_password, user.hashed_password):
            raise InvalidInputError(message="New password must be different from current password")
        self._validate_password_policy(data.new_password, email)
        return {"hashed_password": self._password_service.hash_password(data.new_password)}

    async def update_current_user(self, user: UserRecord, data: UpdateCurrentUserCommand) -> UserRecord:
        self.validate_update_request(data)
        async with self._unit_of_work:
            email, changes = await self._build_email_change(user, data.email)
            changes.update(self._build_profile_changes(user, data))
            await self._update_firm(user, data.firm_name)
            changes.update(self._build_password_change(user, data, email))
            if not changes and data.firm_name is None:
                raise InvalidInputError(message="No changes detected")
            return await self._repository.update_user(user.id, **changes) if changes else user
