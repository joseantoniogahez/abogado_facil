from pydantic import ConfigDict, Field

from app.core.common.schema import ApplicationSchema


class LoginCommand(ApplicationSchema):
    email: str
    password: str


class RegisterUserCommand(ApplicationSchema):
    first_name: str
    middle_name: str | None = None
    last_name: str
    display_name: str
    email: str
    firm_name: str | None = None
    password: str


class UpdateCurrentUserCommand(ApplicationSchema):
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    email: str | None = None
    firm_name: str | None = None
    current_password: str | None = None
    new_password: str | None = None


class AccessTokenResult(ApplicationSchema):
    access_token: str
    token_type: str = "bearer"


class AuthenticatedUserResult(ApplicationSchema):
    id: int
    email: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    display_name: str
    firm_name: str
    disabled: bool
    permissions: tuple[str, ...] = Field(default_factory=tuple)

    model_config = ConfigDict(frozen=True, from_attributes=True)


class AccessTokenPayload(ApplicationSchema):
    sub: str = Field(min_length=1, max_length=255)
    iss: str = Field(min_length=1, max_length=255)
    aud: str = Field(min_length=1, max_length=255)
    iat: int
    exp: int
    jti: str = Field(min_length=1, max_length=255)
    rbac_version: str = Field(min_length=64, max_length=64)
