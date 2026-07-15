from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_matter_note_crud_and_firm_isolation(mock_client: TestClient) -> None:
    reader = _headers(mock_client, "reader@example.com", "reader123")
    admin = _headers(mock_client, "admin@example.com", "admin123")
    client_id = mock_client.post(
        "/v1/clients", headers=reader, json={"full_name": "Ana", "phone": "5512345678"}
    ).json()["id"]
    matter_id = mock_client.post(
        "/v1/matters", headers=reader, json={"client_id": client_id, "title": "Civil", "matter_type": "Otro"}
    ).json()["id"]
    created = mock_client.post(
        f"/v1/matters/{matter_id}/notes", headers=reader, json={"content": "  Llamada inicial  "}
    )
    assert created.status_code == HTTPStatus.CREATED
    note_id = created.json()["id"]
    assert created.json()["content"] == "Llamada inicial"
    assert "firm_id" not in created.json()
    assert mock_client.get(f"/v1/matters/{matter_id}/notes", headers=reader).json()["total"] == 1
    updated = mock_client.patch(f"/v1/matters/{matter_id}/notes/{note_id}", headers=reader, json={"is_relevant": True})
    assert updated.json()["is_relevant"] is True
    assert mock_client.get(f"/v1/matters/{matter_id}/notes", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.patch(
            f"/v1/matters/{matter_id}/notes/{note_id}", headers=admin, json={"is_relevant": False}
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.delete(f"/v1/matters/{matter_id}/notes/{note_id}", headers=reader).status_code
        == HTTPStatus.NO_CONTENT
    )


def test_matter_notes_validate_and_require_auth(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/matters/1/notes").status_code == HTTPStatus.UNAUTHORIZED
    headers = _headers(mock_client, "reader@example.com", "reader123")
    assert (
        mock_client.post("/v1/matters/1/notes", headers=headers, json={"content": " "}).status_code
        == HTTPStatus.BAD_REQUEST
    )
    assert mock_client.patch("/v1/matters/1/notes/1", headers=headers, json={}).status_code == HTTPStatus.BAD_REQUEST
