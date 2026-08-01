from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient) -> dict[str, str]:
    token = client.post(
        "/v1/token",
        data={"username": "reader@example.com", "password": "reader123"},  # pragma: allowlist secret
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_document_template_catalog_is_authenticated_and_complete(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/document-templates").status_code == HTTPStatus.UNAUTHORIZED

    response = mock_client.get("/v1/document-templates", headers=_headers(mock_client))

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert payload["generation_available"] is False
    assert [item["key"] for item in payload["items"]] == [
        "payment_demand",
        "payment_agreement",
        "document_request",
        "internal_matter_summary",
    ]
    assert all(item["fields"] for item in payload["items"])
    assert any(field["required"] is False for item in payload["items"] for field in item["fields"])
