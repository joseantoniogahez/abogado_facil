import asyncio
from http import HTTPStatus
from unittest.mock import AsyncMock

from starlette.testclient import TestClient

from app.features.auth.principal import CurrentPrincipal
from app.features.dashboard.router import get_dashboard_summary


def _auth_headers(mock_client: TestClient, email: str, password: str) -> dict[str, str]:
    response = mock_client.post("/v1/token", data={"username": email, "password": password})
    assert response.status_code == HTTPStatus.OK
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_dashboard_requires_authentication(mock_client: TestClient) -> None:
    response = mock_client.get("/v1/dashboard")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_dashboard_uses_firm_from_authenticated_session(mock_client: TestClient) -> None:
    response = mock_client.get(
        "/v1/dashboard",
        headers=_auth_headers(mock_client, "reader@example.com", "reader123"),
    )

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert payload["firm_id"] > 0
    assert payload["firm_name"]
    assert payload["clients"] == {"value": 0, "available": True}
    assert payload["upcoming_tasks"] == []
    assert payload["ai_status"] == "not_available"


def test_dashboard_rejects_client_selected_firm_parameter_by_ignoring_it(mock_client: TestClient) -> None:
    headers = _auth_headers(mock_client, "reader@example.com", "reader123")
    canonical = mock_client.get("/v1/dashboard", headers=headers).json()

    response = mock_client.get("/v1/dashboard?firm_id=999999", headers=headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["firm_id"] == canonical["firm_id"]


def test_dashboard_rejects_authenticated_principal_without_firm() -> None:
    principal = CurrentPrincipal(
        id=1,
        email="orphan@example.com",
        first_name="Orphan",
        last_name="User",
        display_name="Orphan User",
        disabled=False,
        firm_id=None,
    )
    auth_service = AsyncMock()
    auth_service.get_authenticated_user.return_value.firm_name = "Missing Firm"
    dashboard_service = AsyncMock()

    async def run_test() -> None:
        try:
            await get_dashboard_summary(principal, auth_service, dashboard_service)
        except ValueError as error:
            assert str(error) == "Authenticated dashboard users must belong to a firm"
        else:
            raise AssertionError("Expected a missing-firm principal to be rejected")

    asyncio.run(run_test())
