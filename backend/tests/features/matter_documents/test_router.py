from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _matter(client: TestClient, headers: dict[str, str]) -> int:
    client_id = client.post(
        "/v1/clients", headers=headers, json={"full_name": "Document Owner", "phone": "5512345678"}
    ).json()["id"]
    return client.post(
        "/v1/matters",
        headers=headers,
        json={"client_id": client_id, "title": "Document case", "matter_type": "Otro"},
    ).json()["id"]


def test_document_upload_list_download_delete_and_isolation(mock_client: TestClient) -> None:
    reader = _headers(mock_client, "reader@example.com", "reader123")
    admin = _headers(mock_client, "admin@example.com", "admin123")
    matter_id = _matter(mock_client, reader)
    body = "Acta válida".encode()

    created = mock_client.post(
        f"/v1/matters/{matter_id}/documents",
        headers=reader,
        data={"document_type": "record"},
        files={"file": ("../acta.txt", body, "text/plain")},
    )
    assert created.status_code == HTTPStatus.CREATED
    payload = created.json()
    document_id = payload["id"]
    assert payload["original_filename"] == "acta.txt"
    assert "firm_id" not in payload and "storage_key" not in payload

    listed = mock_client.get(f"/v1/matters/{matter_id}/documents", headers=reader)
    assert listed.json()["total"] == 1
    downloaded = mock_client.get(f"/v1/matters/{matter_id}/documents/{document_id}/download", headers=reader)
    assert downloaded.content == body
    assert downloaded.headers["content-disposition"].startswith("attachment;")
    assert mock_client.get(f"/v1/matters/{matter_id}/documents", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.get(f"/v1/matters/{matter_id}/documents/{document_id}/download", headers=admin).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.post(
            f"/v1/matters/{matter_id}/documents",
            headers=admin,
            data={"document_type": "record"},
            files={"file": ("foreign.txt", b"foreign", "text/plain")},
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.delete(f"/v1/matters/{matter_id}/documents/{document_id}", headers=admin).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.delete(f"/v1/matters/{matter_id}/documents/{document_id}", headers=reader).status_code
        == HTTPStatus.NO_CONTENT
    )


def test_document_upload_rejects_invalid_files_and_requires_auth(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/matters/1/documents").status_code == HTTPStatus.UNAUTHORIZED
    headers = _headers(mock_client, "reader@example.com", "reader123")
    matter_id = _matter(mock_client, headers)
    invalid = mock_client.post(
        f"/v1/matters/{matter_id}/documents",
        headers=headers,
        data={"document_type": "other"},
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
    )
    assert invalid.status_code == HTTPStatus.BAD_REQUEST
    assert invalid.json()["code"] == "invalid_input"
    assert mock_client.get(f"/v1/matters/{matter_id}/documents", headers=headers).json()["total"] == 0
