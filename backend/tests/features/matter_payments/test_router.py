from http import HTTPStatus

from starlette.testclient import TestClient


def _headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_matter_payments_summary_updates_records_and_isolates_firms(mock_client: TestClient) -> None:
    reader = _headers(mock_client, "reader@example.com", "reader123")
    admin = _headers(mock_client, "admin@example.com", "admin123")
    client_id = mock_client.post(
        "/v1/clients", headers=reader, json={"full_name": "Ana", "phone": "5512345678"}
    ).json()["id"]
    matter_id = mock_client.post(
        "/v1/matters",
        headers=reader,
        json={"client_id": client_id, "title": "Cobranza", "matter_type": "Cobro de deuda"},
    ).json()["id"]

    initial = mock_client.get(f"/v1/matters/{matter_id}/payments", headers=reader)
    assert initial.status_code == HTTPStatus.OK
    assert initial.json()["balance"] == "0.00"

    billing = mock_client.put(
        f"/v1/matters/{matter_id}/payments",
        headers=reader,
        json={"agreed_fee": "10000.00", "notes": "  Pago mensual  "},
    )
    assert billing.json()["notes"] == "Pago mensual"
    recorded = mock_client.post(
        f"/v1/matters/{matter_id}/payments",
        headers=reader,
        json={"amount": "2500.50", "payment_type": "advance", "paid_on": "2026-07-16", "note": " Transferencia "},
    )
    assert recorded.status_code == HTTPStatus.CREATED
    assert recorded.json()["total_paid"] == "2500.50"
    assert recorded.json()["balance"] == "7499.50"
    assert recorded.json()["payments"][0]["note"] == "Transferencia"
    assert mock_client.get(f"/v1/matters/{matter_id}/payments", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert (
        mock_client.put(
            f"/v1/matters/{matter_id}/payments",
            headers=admin,
            json={"agreed_fee": "1.00", "notes": None},
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert (
        mock_client.post(
            f"/v1/matters/{matter_id}/payments",
            headers=admin,
            json={"amount": "1.00", "payment_type": "partial", "paid_on": "2026-07-16"},
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_matter_payments_validate_and_require_auth(mock_client: TestClient) -> None:
    assert mock_client.get("/v1/matters/1/payments").status_code == HTTPStatus.UNAUTHORIZED
    headers = _headers(mock_client, "reader@example.com", "reader123")
    assert (
        mock_client.put("/v1/matters/1/payments", headers=headers, json={"agreed_fee": "-1", "notes": None}).status_code
        == HTTPStatus.BAD_REQUEST
    )
    assert (
        mock_client.post(
            "/v1/matters/1/payments",
            headers=headers,
            json={"amount": "0", "payment_type": "advance", "paid_on": "2026-07-16"},
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )
