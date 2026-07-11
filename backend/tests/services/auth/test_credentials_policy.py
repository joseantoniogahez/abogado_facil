from typing import cast

import pytest

from app.core.errors.services import InvalidInputError
from app.core.security.policies import normalize_required_name
from utils.testing_support.auth_service import build_service


def test_normalize_email_trims_and_lowercases() -> None:
    service, _ = build_service()

    normalized = service._normalize_email("  John.Doe+1@Example.COM  ")

    assert normalized == "john.doe+1@example.com"


def test_normalize_email_raises_for_blank_value() -> None:
    service, _ = build_service()

    with pytest.raises(InvalidInputError) as exc_info:
        service._normalize_email("   ")

    assert "Email is required" in str(exc_info.value)


def test_normalize_email_raises_for_invalid_format() -> None:
    service, _ = build_service()

    with pytest.raises(InvalidInputError) as exc_info:
        service._normalize_email("john doe")

    assert "Email has invalid format" in str(exc_info.value)


def test_normalize_required_name_rejects_whitespace_only_value() -> None:
    with pytest.raises(ValueError, match="Display name is required"):
        normalize_required_name("   ", field_name="Display name")


def test_validate_password_policy_raises_with_all_violations() -> None:
    service, _ = build_service()

    with pytest.raises(InvalidInputError) as exc_info:
        service._validate_password_policy("short", "john@example.com")

    details = cast(dict[str, list[str]], exc_info.value.details)
    violations = details["violations"]
    assert "Password must be at least 8 characters long" in violations
    assert "Password must include at least one uppercase letter" in violations
    assert "Password must include at least one number" in violations


def test_validate_password_policy_catches_lowercase_and_identity_rules() -> None:
    service, _ = build_service()

    with pytest.raises(InvalidInputError) as exc_info:
        service._validate_password_policy("JOHN@EXAMPLE.COM1", "john@example.com")

    details = cast(dict[str, list[str]], exc_info.value.details)
    violations = details["violations"]
    assert "Password must include at least one lowercase letter" in violations
    assert "Password cannot contain the username" in violations
