from pydantic import ConfigDict

from app.core.common.schema import ApplicationSchema


class UserRecord(ApplicationSchema):
    id: int
    email: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    display_name: str
    hashed_password: str
    disabled: bool
    firm_id: int | None = None

    model_config = ConfigDict(frozen=True, from_attributes=True)


class FirmRecord(ApplicationSchema):
    id: int
    name: str

    model_config = ConfigDict(frozen=True, from_attributes=True)


class RoleRecord(ApplicationSchema):
    id: int
    name: str

    model_config = ConfigDict(frozen=True, from_attributes=True)


class PermissionRecord(ApplicationSchema):
    id: str
    name: str

    model_config = ConfigDict(frozen=True, from_attributes=True)


class RolePermissionRecord(ApplicationSchema):
    role_id: int
    permission_id: str
    scope: str

    model_config = ConfigDict(frozen=True, from_attributes=True)


class RoleInheritanceRecord(ApplicationSchema):
    role_id: int
    parent_role_id: int

    model_config = ConfigDict(frozen=True, from_attributes=True)
