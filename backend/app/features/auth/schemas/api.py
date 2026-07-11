from typing import Literal

from pydantic import ConfigDict, Field

from app.core.common.schema import ApiSchema


class LoginCredentialsRequest(ApiSchema):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class AccessTokenResponse(ApiSchema):
    access_token: str = Field(min_length=1)
    token_type: Literal["bearer"] = "bearer"


class AuthenticatedUserResponse(ApiSchema):
    id: int
    email: str = Field(min_length=3, max_length=320)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=255)
    firm_name: str = Field(min_length=1, max_length=255)
    disabled: bool
    permissions: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RegisterUserRequest(ApiSchema):
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=320)
    firm_name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=255)

    model_config = ConfigDict(str_strip_whitespace=True)


class UpdateCurrentUserRequest(ApiSchema):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=320)
    firm_name: str | None = Field(default=None, min_length=1, max_length=255)
    current_password: str | None = Field(default=None, min_length=1, max_length=255)
    new_password: str | None = Field(default=None, min_length=8, max_length=255)

    model_config = ConfigDict(str_strip_whitespace=True)
