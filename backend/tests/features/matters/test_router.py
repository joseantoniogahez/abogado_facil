from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_matter_crud_and_firm_isolation(mock_client: TestClient) -> None:
    reader = _headers(mock_client, "reader@example.com", "reader123")
    admin = _headers(mock_client, "admin@example.com", "admin123")
    client_id = mock_client.post(
        "/v1/clients", headers=reader, json={"full_name": "Ana", "phone": "5512345678"}
    ).json()["id"]
    created = mock_client.post(
        "/v1/matters",
        headers=reader,
        json={
            "client_id": client_id,
            "title": "Pensión",
            "matter_type": "Pensión alimenticia",
            "next_action": "Pedir actas",
        },
    )
    assert created.status_code == HTTPStatus.CREATED
    matter_id = created.json()["id"]
    assert "firm_id" not in created.json()
    assert mock_client.get(f"/v1/matters?client_id={client_id}", headers=reader).json()["total"] == 1
    assert (
        mock_client.patch(f"/v1/matters/{matter_id}", headers=reader, json={"status": "closed"}).json()["status"]
        == "closed"
    )
    assert mock_client.get(f"/v1/matters/{matter_id}", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert mock_client.delete(f"/v1/matters/{matter_id}", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.post(
            "/v1/matters", headers=admin, json={"client_id": client_id, "title": "Ajeno", "matter_type": "Otro"}
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert mock_client.delete(f"/v1/matters/{matter_id}", headers=reader).status_code == HTTPStatus.NO_CONTENT
    assert mock_client.get(f"/v1/matters/{matter_id}", headers=reader).status_code == HTTPStatus.NOT_FOUND


def test_matters_require_auth_and_validate_payload(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/matters").status_code == HTTPStatus.UNAUTHORIZED
    headers = _headers(mock_client, "reader@example.com", "reader123")
    assert (
        mock_client.post(
            "/v1/matters", headers=headers, json={"client_id": 1, "title": "", "matter_type": ""}
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )
    assert mock_client.get("/v1/matters/types").status_code == HTTPStatus.UNAUTHORIZED
    catalog = mock_client.get("/v1/matters/types", headers=headers)
    assert catalog.status_code == HTTPStatus.OK
    assert [item["value"] for item in catalog.json()][-1] == "Otro"
    assert (
        mock_client.post(
            "/v1/matters", headers=headers, json={"client_id": 1, "title": "Civil", "matter_type": "Civil"}
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )
