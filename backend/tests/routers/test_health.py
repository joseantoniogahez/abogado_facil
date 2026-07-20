from http import HTTPStatus
from unittest.mock import AsyncMock

from starlette.testclient import TestClient

from app.integrations.files import FileStorageError


def test_health_returns_ok(mock_client: TestClient) -> None:
    response = mock_client.get("/v1/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


def test_readiness_returns_dependency_status(mock_client: TestClient) -> None:
    response = mock_client.get("/v1/readiness")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "status": "ready",
        "checks": {"database": "ok", "object_storage": "ok"},
    }


def test_readiness_returns_safe_503_when_storage_is_unavailable(
    mock_client: TestClient,
    fake_file_storage: object,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        fake_file_storage,
        "check",
        AsyncMock(side_effect=FileStorageError("provider details must stay hidden")),
    )

    response = mock_client.get("/v1/readiness")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {
        "status": "not_ready",
        "checks": {"database": "ok", "object_storage": "unavailable"},
    }
