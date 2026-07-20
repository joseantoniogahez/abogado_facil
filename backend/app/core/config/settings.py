import os
from typing import ClassVar

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    _PRODUCTION_ENV_VALUES: ClassVar[set[str]] = {"prod", "production", "staging"}

    APP_ENV: str = "local"
    API_PATH: str = ""
    API_CORS_ORIGINS: str = ""
    LOG_LEVEL: str = "WARNING"

    @field_validator("APP_ENV")
    @classmethod
    def normalize_app_env(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            return "local"
        return normalized

    @property
    def openapi_enabled(self) -> bool:
        return self.APP_ENV not in self._PRODUCTION_ENV_VALUES


class AuthSettings(BaseSettings):
    _INSECURE_SECRET_VALUES: ClassVar[set[str]] = {
        "change-me-in-production",
        "changeme",
        "secret",
        "default",
        "password",
        "local-dev-jwt-secret",
        "local-dev-jwt-secret-change-me-now",
    }
    _PRODUCTION_ENV_VALUES: ClassVar[set[str]] = {"prod", "production", "staging"}
    _JWT_REQUIRED_ENV_VARS: ClassVar[tuple[str, ...]] = (
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "JWT_ISSUER",
        "JWT_AUDIENCE",
    )

    APP_ENV: str = "local"
    JWT_SECRET_KEY: str = "local-dev-jwt-secret-change-me-now"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, gt=0)
    JWT_ISSUER: str = "abogado-facil"
    JWT_AUDIENCE: str = "abogado-facil-api"

    @field_validator("APP_ENV")
    @classmethod
    def normalize_app_env(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            return "local"
        return normalized

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("JWT_SECRET_KEY cannot be empty.")
        return normalized

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("JWT_ALGORITHM cannot be empty.")
        return normalized

    @field_validator("JWT_ISSUER", "JWT_AUDIENCE")
    @classmethod
    def validate_jwt_identity_claim(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("JWT issuer and audience cannot be empty.")
        return normalized

    @classmethod
    def _is_missing_env_var(cls, name: str) -> bool:
        value = os.getenv(name)
        return value is None or not value.strip()

    @model_validator(mode="after")
    def validate_production_jwt_requirements(self) -> AuthSettings:
        if self.APP_ENV not in self._PRODUCTION_ENV_VALUES:
            return self

        missing = [name for name in self._JWT_REQUIRED_ENV_VARS if self._is_missing_env_var(name)]
        if missing:
            missing_vars = ", ".join(sorted(missing))
            raise ValueError(f"Missing required JWT environment variables for production: {missing_vars}.")

        if self.JWT_SECRET_KEY.lower() in self._INSECURE_SECRET_VALUES:
            raise ValueError("JWT_SECRET_KEY contains an insecure placeholder value.")

        return self


class DatabaseSettings(BaseSettings):
    DB_TYPE: str = "sqlite+aiosqlite"
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str = "app.db"


class ObjectStorageSettings(BaseSettings):
    S3_ENDPOINT_URL: str
    S3_REGION: str
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: SecretStr
    S3_PATH_STYLE: bool = True
    S3_CONNECT_TIMEOUT_SECONDS: float = Field(3.0, gt=0)
    S3_READ_TIMEOUT_SECONDS: float = Field(10.0, gt=0)

    @field_validator("S3_ENDPOINT_URL", "S3_REGION", "S3_BUCKET", "S3_ACCESS_KEY")
    @classmethod
    def reject_blank_storage_values(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Object storage configuration values cannot be empty.")
        return normalized

    @model_validator(mode="after")
    def validate_storage_configuration(self) -> ObjectStorageSettings:
        if not self.S3_ENDPOINT_URL.startswith(("http://", "https://")):
            raise ValueError("S3_ENDPOINT_URL must use http:// or https://.")
        if not self.S3_SECRET_KEY.get_secret_value().strip():
            raise ValueError("S3_SECRET_KEY cannot be empty.")
        return self


class MatterDocumentSettings(BaseSettings):
    MATTER_DOCUMENT_MAX_SIZE_BYTES: int = Field(10 * 1024 * 1024, gt=0)
    MATTER_DOCUMENT_MAX_PER_MATTER: int = Field(50, gt=0)
