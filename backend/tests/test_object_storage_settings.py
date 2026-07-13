import pytest
from pydantic import ValidationError

from app.core.config.settings import ObjectStorageSettings
from app.core.setup.factory import validate_object_storage_settings


def test_object_storage_settings_accept_explicit_environment_and_redact_secret() -> None:
    settings = ObjectStorageSettings()
    assert settings.S3_PATH_STYLE is True
    assert "minioadmin" not in repr(settings.S3_SECRET_KEY)


@pytest.mark.parametrize("field", ["S3_ENDPOINT_URL", "S3_REGION", "S3_BUCKET", "S3_ACCESS_KEY"])
def test_object_storage_settings_reject_blank_values(field: str) -> None:
    with pytest.raises(ValidationError):
        ObjectStorageSettings.model_validate({field: " "})


def test_object_storage_settings_reject_invalid_endpoint_and_blank_secret() -> None:
    with pytest.raises(ValidationError, match="http"):
        ObjectStorageSettings(S3_ENDPOINT_URL="ftp://storage")
    with pytest.raises(ValidationError, match="S3_SECRET_KEY"):
        ObjectStorageSettings(S3_SECRET_KEY=" ")


def test_object_storage_settings_require_all_environment_values(monkeypatch: pytest.MonkeyPatch) -> None:
    required_names = (
        "S3_ENDPOINT_URL",
        "S3_REGION",
        "S3_BUCKET",
        "S3_ACCESS_KEY",
        "S3_SECRET_KEY",
    )
    for name in required_names:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValidationError) as exc_info:
        ObjectStorageSettings()

    message = str(exc_info.value)
    for name in required_names:
        assert name in message


def test_startup_validation_wraps_details_without_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("S3_ENDPOINT_URL", "invalid-secret-endpoint")
    with pytest.raises(RuntimeError) as exc_info:
        validate_object_storage_settings()
    assert "invalid-secret-endpoint" not in str(exc_info.value)
