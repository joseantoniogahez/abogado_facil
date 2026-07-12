from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/v1/token", data={"username": email, "password": password})
    assert response.status_code == HTTPStatus.OK
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_clients_require_authentication(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/clients").status_code == HTTPStatus.UNAUTHORIZED


def test_client_crud_search_and_firm_isolation(mock_client: TestClient) -> None:
    reader = _headers(mock_client, "reader@example.com", "reader123")
    admin = _headers(mock_client, "admin@example.com", "admin123")
    created = mock_client.post(
        "/v1/clients",
        headers=reader,
        json={"full_name": "María López", "phone": "+52 (55) 1234-5678", "email": "maria@example.com"},
    )
    assert created.status_code == HTTPStatus.CREATED
    client_id = created.json()["id"]
    assert "firm_id" not in created.json()
    assert created.json()["phone"] == "5512345678"

    found = mock_client.get("/v1/clients?search=%2B52%2055%201234%205678", headers=reader)
    assert found.status_code == HTTPStatus.OK
    assert found.json()["total"] == 1
    assert found.json()["items"][0]["full_name"] == "María López"

    detail = mock_client.get(f"/v1/clients/{client_id}", headers=reader)
    assert detail.status_code == HTTPStatus.OK
    updated = mock_client.patch(
        f"/v1/clients/{client_id}", headers=reader, json={"notes": "Prefiere llamadas por la tarde"}
    )
    assert updated.status_code == HTTPStatus.OK
    assert updated.json()["notes"] == "Prefiere llamadas por la tarde"

    assert mock_client.get(f"/v1/clients/{client_id}", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.patch(f"/v1/clients/{client_id}", headers=admin, json={"phone": "5512345678"}).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert mock_client.get("/v1/clients", headers=admin).json()["total"] == 0


def test_client_payload_rejects_blank_required_fields(mock_client: TestClient) -> None:
    headers = _headers(mock_client, "reader@example.com", "reader123")
    response = mock_client.post("/v1/clients", headers=headers, json={"full_name": "", "phone": ""})
    assert response.status_code == HTTPStatus.BAD_REQUEST
