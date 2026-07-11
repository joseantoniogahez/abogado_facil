from typing import Any, Protocol

from app.core.authorization import PermissionScope
from app.core.authorization.permission_evaluator import PermissionEvaluator, PermissionEvaluatorPort
from app.core.common.records import FirmRecord, UserRecord
from app.core.config.settings import AuthSettings
from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import ConflictError, ForbiddenError, InvalidInputError, UnauthorizedError
from app.core.security.policies import (
    PasswordPolicyError,
    format_password_policy_messages,
    normalize_email,
    normalize_required_name,
    validate_password_policy,
)
from app.core.security.service import Argon2PasswordService, JwtTokenService, PasswordServicePort, TokenServicePort
from app.features.auth.principal import CurrentPrincipal
from app.features.auth.profile_updates import AuthProfileUpdates
from app.features.auth.schemas import (
    AccessTokenResult,
    AuthenticatedUserResult,
    LoginCommand,
    RegisterUserCommand,
    UpdateCurrentUserCommand,
)

PermissionScopeCache = dict[tuple[int, str], str | None]


class AuthRepositoryPort(Protocol):
    async def get_by_email(self, email: str) -> UserRecord | None: ...

    async def email_exists(self, email: str, *, exclude_user_id: int | None = None) -> bool: ...

    async def create_user(self, **kwargs: Any) -> UserRecord: ...

    async def update_user(self, user_id: int, **changes: Any) -> UserRecord: ...
    async def create_firm(self, *, name: str) -> FirmRecord: ...
    async def get_firm(self, firm_id: int) -> FirmRecord | None: ...
    async def update_firm(self, firm_id: int, *, name: str) -> FirmRecord: ...
    async def assign_role_by_name(self, *, user_id: int, role_name: str) -> None: ...

    async def get_rbac_version(self, user_id: int) -> str: ...

    async def get_user_effective_permission_ids(self, user_id: int) -> tuple[str, ...]: ...

    async def get_user_permission_scope(self, user_id: int, permission_id: str) -> str | None: ...

    async def user_has_permission(self, user_id: int, permission_id: str) -> bool: ...


class AuthServicePort(Protocol):
    async def login(self, credentials: LoginCommand) -> AccessTokenResult: ...

    async def register(self, registration: RegisterUserCommand) -> AuthenticatedUserResult: ...

    async def update_current_user(
        self,
        current_user: CurrentPrincipal,
        update_data: UpdateCurrentUserCommand,
    ) -> AuthenticatedUserResult: ...

    async def get_authenticated_user(self, current_user: CurrentPrincipal) -> AuthenticatedUserResult: ...

    async def get_user_from_token(self, token: str) -> CurrentPrincipal: ...

    async def user_has_permission(
        self,
        user_id: int,
        permission_id: str,
        *,
        required_scope: str = PermissionScope.ANY,
        resource_owner_id: int | None = None,
        resource_tenant_id: int | None = None,
        user_tenant_id: int | None = None,
    ) -> bool: ...


class AuthService:
    def __init__(
        self,
        auth_repository: AuthRepositoryPort,
        unit_of_work: UnitOfWorkPort,
        auth_settings: AuthSettings | None = None,
        permission_evaluator: PermissionEvaluatorPort | None = None,
        token_service: TokenServicePort | None = None,
        password_service: PasswordServicePort | None = None,
        permission_scope_cache: PermissionScopeCache | None = None,
    ):
        settings = auth_settings or AuthSettings()
        self.auth_repository = auth_repository
        self.unit_of_work = unit_of_work
        self.permission_evaluator = permission_evaluator or PermissionEvaluator()
        self.token_service = token_service or JwtTokenService(settings)
        self.password_service = password_service or Argon2PasswordService()
        self.permission_scope_cache = permission_scope_cache
        self._profile_updates = AuthProfileUpdates(
            auth_repository=auth_repository,
            unit_of_work=unit_of_work,
            password_service=self.password_service,
            normalize_email=self._normalize_email,
            validate_password_policy=self._validate_password_policy,
        )

    def _normalize_email(self, email: str) -> str:
        try:
            return normalize_email(email)
        except ValueError as exc:
            raise InvalidInputError(message=str(exc)) from exc

    def _validate_password_policy(self, password: str, username: str) -> None:
        try:
            validate_password_policy(password, username)
        except PasswordPolicyError as exc:
            raise InvalidInputError(
                message="Password does not meet policy",
                details={"violations": format_password_policy_messages(exc.violations)},
            ) from exc

    async def _authenticate_or_raise(self, credentials: LoginCommand) -> UserRecord:
        email = self._normalize_email(credentials.email)
        user = await self.auth_repository.get_by_email(email)
        if user is None or not self.password_service.verify_password(credentials.password, user.hashed_password):
            raise UnauthorizedError(message="Invalid email or password")

        if user.disabled:
            raise ForbiddenError(message="Inactive user")

        return user

    async def login(self, credentials: LoginCommand) -> AccessTokenResult:
        user = await self._authenticate_or_raise(credentials)
        rbac_version = await self.auth_repository.get_rbac_version(user.id)
        access_token = self.token_service.encode_access_token(
            subject=user.email,
            rbac_version=rbac_version,
        )
        return AccessTokenResult(access_token=access_token)

    async def register(self, registration: RegisterUserCommand) -> AuthenticatedUserResult:
        email = self._normalize_email(registration.email)
        try:
            first_name = normalize_required_name(registration.first_name, field_name="First name")
            middle_name = (
                normalize_required_name(registration.middle_name, field_name="Middle name")
                if registration.middle_name
                else None
            )
            last_name = normalize_required_name(registration.last_name, field_name="Last name")
            display_name = normalize_required_name(registration.display_name, field_name="Display name")
            firm_name = normalize_required_name(registration.firm_name or display_name, field_name="Firm name")
        except ValueError as exc:
            raise InvalidInputError(message=str(exc)) from exc
        self._validate_password_policy(registration.password, email)

        async with self.unit_of_work:
            if await self.auth_repository.email_exists(email):
                raise ConflictError(
                    message="Email already exists",
                    details={"email": email},
                )
            firm = await self.auth_repository.create_firm(name=firm_name)
            user = await self.auth_repository.create_user(
                email=email,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                display_name=display_name,
                hashed_password=self.password_service.hash_password(registration.password),
                disabled=False,
                firm_id=firm.id,
            )
            await self.auth_repository.assign_role_by_name(user_id=user.id, role_name="account_owner")

        return await self._build_authenticated_user_result(user)

    @staticmethod
    def _normalize_permissions(permission_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        return tuple(sorted(set(permission_ids)))

    async def _load_effective_permission_ids(self, user_id: int) -> tuple[str, ...]:
        repository_attributes = getattr(self.auth_repository, "__dict__", {})
        instance_loader = repository_attributes.get("get_user_effective_permission_ids")
        if instance_loader is not None:
            return self._normalize_permissions(await instance_loader(user_id))

        if not hasattr(type(self.auth_repository), "get_user_effective_permission_ids"):
            return ()

        return await self.auth_repository.get_user_effective_permission_ids(user_id)

    async def _build_authenticated_user_result(self, user: UserRecord | CurrentPrincipal) -> AuthenticatedUserResult:
        permission_ids = await self._load_effective_permission_ids(user.id)
        firm = await self.auth_repository.get_firm(user.firm_id) if user.firm_id is not None else None
        return AuthenticatedUserResult(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            display_name=user.display_name,
            firm_name=firm.name if firm is not None else user.display_name,
            disabled=user.disabled,
            permissions=permission_ids,
        )

    def _validate_update_request(self, update_data: UpdateCurrentUserCommand) -> None:
        self._profile_updates.validate_update_request(update_data)

    async def update_current_user(
        self,
        current_user: CurrentPrincipal,
        update_data: UpdateCurrentUserCommand,
    ) -> AuthenticatedUserResult:
        persisted_user = await self.auth_repository.get_by_email(current_user.email)
        if persisted_user is None:
            raise UnauthorizedError(message="Could not validate credentials")

        updated_user = await self._profile_updates.update_current_user(persisted_user, update_data)
        return await self._build_authenticated_user_result(updated_user)

    async def get_authenticated_user(self, current_user: CurrentPrincipal) -> AuthenticatedUserResult:
        return await self._build_authenticated_user_result(current_user)

    async def get_user_from_token(self, token: str) -> CurrentPrincipal:
        payload = self.token_service.decode_access_token(token)
        if payload is None:
            raise UnauthorizedError(message="Could not validate credentials")

        user = await self.auth_repository.get_by_email(payload.sub)
        if user is None:
            raise UnauthorizedError(message="Could not validate credentials")

        current_rbac_version = await self.auth_repository.get_rbac_version(user.id)
        if payload.rbac_version != current_rbac_version:
            raise UnauthorizedError(message="Could not validate credentials")

        return CurrentPrincipal.from_domain(user)

    async def _get_granted_scope(self, *, user_id: int, permission_id: str) -> str | None:
        if self.permission_scope_cache is None:
            return await self.auth_repository.get_user_permission_scope(
                user_id=user_id,
                permission_id=permission_id,
            )

        cache_key = (user_id, permission_id)
        if cache_key in self.permission_scope_cache:
            return self.permission_scope_cache[cache_key]

        granted_scope = await self.auth_repository.get_user_permission_scope(
            user_id=user_id,
            permission_id=permission_id,
        )
        self.permission_scope_cache[cache_key] = granted_scope
        return granted_scope

    async def user_has_permission(
        self,
        user_id: int,
        permission_id: str,
        *,
        required_scope: str = PermissionScope.ANY,
        resource_owner_id: int | None = None,
        resource_tenant_id: int | None = None,
        user_tenant_id: int | None = None,
    ) -> bool:
        normalized_required_scope = self.permission_evaluator.normalize_required_scope(required_scope)
        granted_scope = await self._get_granted_scope(
            user_id=user_id,
            permission_id=permission_id,
        )
        return self.permission_evaluator.is_granted_scope_allowed(
            granted_scope=granted_scope,
            required_scope=normalized_required_scope,
            user_id=user_id,
            resource_owner_id=resource_owner_id,
            user_tenant_id=user_tenant_id,
            resource_tenant_id=resource_tenant_id,
        )
