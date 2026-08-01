from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_checklist_crud_templates_and_firm_isolation(mock_client: TestClient) -> None:
    reader = _headers(mock_client, "reader@example.com", "reader123")
    admin = _headers(mock_client, "admin@example.com", "admin123")
    client_id = mock_client.post(
        "/v1/clients", headers=reader, json={"full_name": "Ana", "phone": "5512345678"}
    ).json()["id"]
    matter_id = mock_client.post(
        "/v1/matters",
        headers=reader,
        json={"client_id": client_id, "title": "Divorcio", "matter_type": "Divorcio básico"},
    ).json()["id"]

    first = mock_client.get(f"/v1/matters/{matter_id}/checklist", headers=reader)
    assert first.status_code == HTTPStatus.OK
    assert first.json()["total"] == 4
    assert all(item["is_ai_suggested"] is False for item in first.json()["items"])
    assert mock_client.get(f"/v1/matters/{matter_id}/checklist", headers=reader).json()["total"] == 4
    item_id = first.json()["items"][0]["id"]
    updated = mock_client.patch(
        f"/v1/matters/{matter_id}/checklist/{item_id}", headers=reader, json={"status": "complete"}
    )
    assert updated.json()["status"] == "complete"
    custom = mock_client.post(f"/v1/matters/{matter_id}/checklist", headers=reader, json={"label": "  Fotografías  "})
    assert custom.status_code == HTTPStatus.CREATED
    assert custom.json()["label"] == "Fotografías"
    assert custom.json()["is_custom"] is True
    assert custom.json()["is_ai_suggested"] is False
    assert mock_client.get(f"/v1/matters/{matter_id}/checklist", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.post(
            f"/v1/matters/{matter_id}/checklist", headers=admin, json={"label": "Foreign write"}
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.patch(
            f"/v1/matters/{matter_id}/checklist/{item_id}",
            headers=admin,
            json={"status": "not_applicable"},
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_checklist_validates_and_requires_auth(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/matters/1/checklist").status_code == HTTPStatus.UNAUTHORIZED
    headers = _headers(mock_client, "reader@example.com", "reader123")
    assert (
        mock_client.post("/v1/matters/1/checklist", headers=headers, json={"label": " "}).status_code
        == HTTPStatus.BAD_REQUEST
    )
    assert (
        mock_client.patch("/v1/matters/1/checklist/1", headers=headers, json={"status": "invalid"}).status_code
        == HTTPStatus.BAD_REQUEST
    )
