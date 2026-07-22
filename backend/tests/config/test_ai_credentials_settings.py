import base64

import pytest
from pydantic import ValidationError

from app.core.config.settings import AiCredentialSettings


def test_ai_credential_settings_reject_invalid_key() -> None:
    with pytest.raises(ValidationError):
        AiCredentialSettings(AI_CREDENTIAL_ENCRYPTION_KEY="invalid")


def test_ai_credential_settings_rejects_malformed_base64_key() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(base64, "urlsafe_b64decode", lambda _: (_ for _ in ()).throw(ValueError("bad")))
        with pytest.raises(ValidationError, match="urlsafe base64"):
            AiCredentialSettings(AI_CREDENTIAL_ENCRYPTION_KEY="a")


def test_ai_credential_settings_rejects_wrong_decoded_key_length() -> None:
    key = base64.urlsafe_b64encode(b"x" * 31).decode()
    with pytest.raises(ValidationError, match="32 bytes"):
        AiCredentialSettings(AI_CREDENTIAL_ENCRYPTION_KEY=key)


def test_ai_credential_settings_require_production_environment_key(monkeypatch) -> None:
    monkeypatch.delenv("AI_CREDENTIAL_ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValidationError):
        AiCredentialSettings(APP_ENV="prod")
