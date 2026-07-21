import pytest
from pydantic import ValidationError

from app.core.config.settings import AiCredentialSettings


def test_ai_credential_settings_reject_invalid_key() -> None:
    with pytest.raises(ValidationError):
        AiCredentialSettings(AI_CREDENTIAL_ENCRYPTION_KEY="invalid")


def test_ai_credential_settings_require_production_environment_key(monkeypatch) -> None:
    monkeypatch.delenv("AI_CREDENTIAL_ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        AiCredentialSettings(APP_ENV="prod")
