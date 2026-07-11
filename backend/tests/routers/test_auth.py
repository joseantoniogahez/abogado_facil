import hashlib
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Any

import jwt
from starlette.testclient import TestClient

from app.core.authorization import PERMISSION_SPECS
from app.core.config.settings import AuthSettings
from utils.testing_support.api_assertions import assert_error_response


def _build_access_token(email: str) -> str:
    settings = AuthSettings()
    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(issued_at.timestamp()),
        "exp": int(expire_at.timestamp()),
        "jti": f"test-{email}",
        "rbac_version": hashlib.sha256(b"").hexdigest(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _assert_error_payload(response: Any, error_type: str, message: str, details: Any | None = None) -> None:
    assert_error_response(
        response,
        detail=message,
        status_code=response.status_code,
        code=error_type,
        meta=details,
    )


def test_token_success(mock_client: TestClient) -> None:
    response = mock_client.post(
        "/v1/token",
        data={
            "username": "admin@example.com",
            "password": "admin123",  # pragma: allowlist secret
        },
    )

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert payload["access_token"]


def test_token_rejects_invalid_credentials_variants(mock_client: TestClient) -> None:
    for credentials in (
        {"username": "admin@example.com", "password": "wrong-password"},  # pragma: allowlist secret
        {"username": "unknown@example.com", "password": "admin123"},  # pragma: allowlist secret
    ):
        response = mock_client.post("/v1/token", data=credentials)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        _assert_error_payload(response, "unauthorized", "Invalid email or password")
        assert response.headers["www-authenticate"] == "Bearer"


def test_token_disabled_user(mock_client: TestClient) -> None:
    response = mock_client.post(
        "/v1/token",
        data={
            "username": "disabled@example.com",
            "password": "admin123",  # pragma: allowlist secret
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    _assert_error_payload(response, "forbidden", "Inactive user")


def test_get_current_active_user(mock_client: TestClient) -> None:
    token_response = mock_client.post(
        "/v1/token",
        data={
            "username": "admin@example.com",
            "password": "admin123",  # pragma: allowlist secret
        },
    )
    access_token = token_response.json()["access_token"]

    response = mock_client.get("/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    expected_permissions = sorted(permission_id for permission_id, _ in PERMISSION_SPECS)
    assert response.json() == {
        "id": 1,
        "email": "admin@example.com",
        "first_name": "Ada",
        "middle_name": None,
        "last_name": "Admin",
        "display_name": "Admin User",
        "firm_name": "Admin Legal",
        "disabled": False,
        "permissions": expected_permissions,
    }


def test_get_current_active_user_rejects_invalid_tokens_and_inactive_user(mock_client: TestClient) -> None:
    authorizations = (
        "Bearer not-a-valid-token",
        f"Bearer {_build_access_token('ghost@example.com')}",
        f"Bearer {_build_access_token('disabled@example.com')}",
    )
    status_codes = (HTTPStatus.UNAUTHORIZED, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
    error_types = ("unauthorized", "unauthorized", "forbidden")
    messages = ("Could not validate credentials", "Could not validate credentials", "Inactive user")
    expects_www_authenticate_values = (True, True, False)

    for authorization, status_code, error_type, message, expects_www_authenticate in zip(
        authorizations, status_codes, error_types, messages, expects_www_authenticate_values, strict=True
    ):
        response = mock_client.get("/v1/users/me", headers={"Authorization": authorization})

        assert response.status_code == status_code
        error_type = error_type
        _assert_error_payload(response, error_type, message)
        if expects_www_authenticate:
            assert response.headers["www-authenticate"] == "Bearer"


def test_register_user_success(mock_client: TestClient) -> None:
    response = mock_client.post(
        "/v1/users/register",
        json={
            "first_name": " New ",
            "middle_name": " Q. ",
            "last_name": " User ",
            "display_name": " New Counsel ",
            "email": " NEW.USER@EXAMPLE.COM ",
            "password": "StrongPass1",  # pragma: allowlist secret
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    payload = response.json()
    assert isinstance(payload["id"], int)
    assert payload == {
        "id": payload["id"],
        "email": "new.user@example.com",
        "first_name": "New",
        "middle_name": "Q.",
        "last_name": "User",
        "display_name": "New Counsel",
        "firm_name": "New Counsel",
        "disabled": False,
        "permissions": [],
    }

    token_response = mock_client.post(
        "/v1/token",
        data={
            "username": "NEW.USER@EXAMPLE.COM",
            "password": "StrongPass1",  # pragma: allowlist secret
        },
    )
    assert token_response.status_code == HTTPStatus.OK


def test_register_user_rejects_common_error_cases(mock_client: TestClient) -> None:
    payloads = (
        {
            "first_name": "Invalid",
            "last_name": "Email",
            "display_name": "Invalid Email",
            "email": "invalid-email",
            "password": "StrongPass1",  # pragma: allowlist secret
        },
        {
            "first_name": "Duplicate",
            "last_name": "Admin",
            "display_name": "Duplicate Admin",
            "email": " ADMIN@EXAMPLE.COM ",
            "password": "StrongPass1",  # pragma: allowlist secret
        },
        {
            "first_name": "Policy",
            "last_name": "User",
            "display_name": "Policy User",
            "email": "policy.user@example.com",
            "password": "onlylowercase1",  # pragma: allowlist secret
        },
    )
    status_codes = (HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.BAD_REQUEST)
    error_types = ("invalid_input", "conflict", "invalid_input")
    messages = ("Email has invalid format", "Email already exists", "Password does not meet policy")
    detail_dicts = (
        None,
        {"email": "admin@example.com"},
        {"violations": ["Password must include at least one uppercase letter"]},
    )

    for payload, status_code, error_type, message, details in zip(
        payloads, status_codes, error_types, messages, detail_dicts, strict=True
    ):
        response = mock_client.post("/v1/users/register", json=payload)

        assert response.status_code == status_code
        _assert_error_payload(
            response,
            error_type,
            message,
            details=details,
        )


def test_register_user_missing_password_returns_normalized_validation_error(mock_client: TestClient) -> None:
    response = mock_client.post(
        "/v1/users/register",
        json={
            "first_name": "Missing",
            "last_name": "Password",
            "display_name": "Missing Password",
            "email": "missing.password@example.com",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    payload = response.json()
    assert payload["detail"] == "Request validation error"
    assert payload["status"] == HTTPStatus.BAD_REQUEST
    assert payload["code"] == "invalid_input"
    assert isinstance(payload.get("request_id"), str)
    assert response.headers["X-Request-ID"] == payload["request_id"]
    assert any(error.get("loc") == ["body", "password"] and error.get("type") == "missing" for error in payload["meta"])


def test_update_current_user_profile_email_firm_and_password(mock_client: TestClient) -> None:
    register_response = mock_client.post(
        "/v1/users/register",
        json={
            "first_name": "Profile",
            "middle_name": "Quinn",
            "last_name": "User",
            "display_name": "Profile User",
            "email": "profile.user@example.com",
            "firm_name": "Profile Legal",
            "password": "ProfilePass1",  # pragma: allowlist secret
        },
    )
    assert register_response.status_code == HTTPStatus.CREATED
    user_id = register_response.json()["id"]

    login_response = mock_client.post(
        "/v1/token",
        data={
            "username": "profile.user@example.com",
            "password": "ProfilePass1",  # pragma: allowlist secret
        },
    )
    assert login_response.status_code == HTTPStatus.OK
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    update_response = mock_client.patch(
        "/v1/users/me",
        headers=headers,
        json={
            "first_name": " Pat ",
            "middle_name": " R. ",
            "last_name": " Updated ",
            "display_name": " Counsel Pat ",
            "email": " PROFILE.UPDATED@EXAMPLE.COM ",
            "firm_name": " Updated Legal ",
            "current_password": "ProfilePass1",  # pragma: allowlist secret
            "new_password": "ProfilePass2",  # pragma: allowlist secret
        },
    )

    assert update_response.status_code == HTTPStatus.OK
    assert update_response.json() == {
        "id": user_id,
        "email": "profile.updated@example.com",
        "first_name": "Pat",
        "middle_name": "R.",
        "last_name": "Updated",
        "display_name": "Counsel Pat",
        "firm_name": "Updated Legal",
        "disabled": False,
        "permissions": [],
    }

    old_login = mock_client.post(
        "/v1/token",
        data={
            "username": "profile.user@example.com",
            "password": "ProfilePass1",  # pragma: allowlist secret
        },
    )
    assert old_login.status_code == HTTPStatus.UNAUTHORIZED

    new_login = mock_client.post(
        "/v1/token",
        data={
            "username": "PROFILE.UPDATED@EXAMPLE.COM",
            "password": "ProfilePass2",  # pragma: allowlist secret
        },
    )
    assert new_login.status_code == HTTPStatus.OK


def test_update_current_user_rejects_invalid_update_payloads(mock_client: TestClient) -> None:
    login_response = mock_client.post(
        "/v1/token",
        data={
            "username": "admin@example.com",
            "password": "admin123",  # pragma: allowlist secret
        },
    )
    assert login_response.status_code == HTTPStatus.OK
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    payloads = (
        {"new_password": "AdminPass9"},  # pragma: allowlist secret
        {"current_password": "admin123"},  # pragma: allowlist secret
        {"email": " ADMIN@EXAMPLE.COM "},
        {"current_password": "admin123", "new_password": "admin123"},  # pragma: allowlist secret
    )
    expected_messages = (
        "current_password is required to update password",
        "new_password is required when current_password is provided",
        "No changes detected",
        "New password must be different from current password",
    )

    for payload, expected_message in zip(payloads, expected_messages, strict=True):
        response = mock_client.patch("/v1/users/me", headers=headers, json=payload)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        _assert_error_payload(response, "invalid_input", expected_message)

    response = mock_client.patch("/v1/users/me", headers=headers, json={})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    _assert_error_payload(response, "invalid_input", "At least one field must be provided to update the user")


def test_update_current_user_rejects_invalid_current_password(mock_client: TestClient) -> None:
    login_response = mock_client.post(
        "/v1/token",
        data={
            "username": "admin@example.com",
            "password": "admin123",  # pragma: allowlist secret
        },
    )
    assert login_response.status_code == HTTPStatus.OK
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response = mock_client.patch(
        "/v1/users/me",
        headers=headers,
        json={
            "current_password": "wrong-password",  # pragma: allowlist secret
            "new_password": "AdminPass9",  # pragma: allowlist secret
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    _assert_error_payload(response, "unauthorized", "Current password is invalid")
    assert response.headers["www-authenticate"] == "Bearer"


def test_update_current_user_email_conflict(mock_client: TestClient) -> None:
    login_response = mock_client.post(
        "/v1/token",
        data={
            "username": "reader@example.com",
            "password": "reader123",  # pragma: allowlist secret
        },
    )
    assert login_response.status_code == HTTPStatus.OK
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response = mock_client.patch(
        "/v1/users/me",
        headers=headers,
        json={"email": " ADMIN@EXAMPLE.COM "},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    _assert_error_payload(
        response,
        "conflict",
        "Email already exists",
        details={"email": "admin@example.com"},
    )
