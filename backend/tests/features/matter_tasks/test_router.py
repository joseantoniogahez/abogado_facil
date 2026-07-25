from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_matter_task_crud_dashboard_and_firm_isolation(mock_client: TestClient) -> None:
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

    created = mock_client.post(
        f"/v1/matters/{matter_id}/tasks",
        headers=reader,
        json={"title": "  Presentar escrito  ", "due_date": "2026-07-20"},
    )
    assert created.status_code == HTTPStatus.CREATED
    assert created.json()["title"] == "Presentar escrito"
    task_id = created.json()["id"]
    assert mock_client.get(f"/v1/matters/{matter_id}/tasks", headers=reader).json()["total"] == 1
    dashboard = mock_client.get("/v1/dashboard", headers=reader).json()
    assert dashboard["pending_tasks"] == {"value": 1, "available": True}
    assert dashboard["upcoming_tasks"][0]["matter_title"] == "Divorcio"

    updated = mock_client.patch(
        f"/v1/matters/{matter_id}/tasks/{task_id}",
        headers=reader,
        json={"completed": True},
    )
    assert updated.json()["completed"] is True
    assert mock_client.get("/v1/dashboard", headers=reader).json()["pending_tasks"]["value"] == 0
    assert mock_client.get(f"/v1/matters/{matter_id}/tasks", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.post(
            f"/v1/matters/{matter_id}/tasks",
            headers=admin,
            json={"title": "Foreign write", "due_date": "2026-07-21"},
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.patch(
            f"/v1/matters/{matter_id}/tasks/{task_id}", headers=admin, json={"completed": False}
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_matter_tasks_validate_and_require_auth(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/matters/1/tasks").status_code == HTTPStatus.UNAUTHORIZED
    headers = _headers(mock_client, "reader@example.com", "reader123")
    assert (
        mock_client.post(
            "/v1/matters/1/tasks", headers=headers, json={"title": " ", "due_date": "2026-07-20"}
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )
    assert mock_client.patch("/v1/matters/1/tasks/1", headers=headers, json={}).status_code == HTTPStatus.BAD_REQUEST
