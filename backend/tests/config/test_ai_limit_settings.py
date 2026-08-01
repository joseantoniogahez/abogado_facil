import pytest
from pydantic import ValidationError

from app.core.config.settings import AILimitSettings


def test_ai_limit_settings_defaults_and_bounds() -> None:
    settings = AILimitSettings()
    assert settings.AI_INPUT_MAX_CHARS == 20_000
    assert settings.AI_OUTPUT_MAX_TOKENS == 1_200
    assert settings.DOCUMENT_DRAFT_FIELD_MAX_CHARS == 20_000
    assert settings.DOCUMENT_DRAFT_OUTPUT_MAX_TOKENS == 1_800

    for values in (
        {"AI_INPUT_MAX_CHARS": 19},
        {"AI_OUTPUT_MAX_TOKENS": 8_001},
        {"DOCUMENT_DRAFT_FIELD_MAX_CHARS": 20_001},
        {"DOCUMENT_DRAFT_OUTPUT_MAX_TOKENS": 0},
    ):
        with pytest.raises(ValidationError):
            AILimitSettings(**values)
