from http import HTTPStatus
from types import SimpleNamespace

import pytest

from app.features.matter_calculations.router import firm_id


def headers(client, email, password):
    token = client.post("/v1/token", data={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_calculations_preview_save_list_and_isolate(mock_client):
    reader = headers(mock_client, "reader@example.com", "reader123")
    admin = headers(mock_client, "admin@example.com", "admin123")
    client_id = mock_client.post(
        "/v1/clients", headers=reader, json={"full_name": "Ana", "phone": "5512345678"}
    ).json()["id"]
    matter_id = mock_client.post(
        "/v1/matters",
        headers=reader,
        json={"client_id": client_id, "title": "Cobranza", "matter_type": "Cobro de deuda"},
    ).json()["id"]
    base = {
        "principal": "10000",
        "payments": "2500",
        "monthly_rent": "4000",
        "overdue_months": 3,
        "annual_rate": "12",
        "days": 30,
    }
    for kind, expected in (("debt_balance", "7500.00"), ("overdue_rent", "9500.00"), ("simple_interest", "98.63")):
        response = mock_client.post(
            f"/v1/matters/{matter_id}/calculations/preview", headers=reader, json={**base, "calculation_type": kind}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["result_amount"] == expected
    saved = mock_client.post(
        f"/v1/matters/{matter_id}/calculations", headers=reader, json={**base, "calculation_type": "debt_balance"}
    )
    assert saved.status_code == HTTPStatus.CREATED
    assert (
        mock_client.get(f"/v1/matters/{matter_id}/calculations", headers=reader).json()["items"][0]["id"]
        == saved.json()["id"]
    )
    assert mock_client.get(f"/v1/matters/{matter_id}/calculations", headers=admin).status_code == HTTPStatus.NOT_FOUND
    assert mock_client.get(f"/v1/matters/{matter_id}/calculations").status_code == HTTPStatus.UNAUTHORIZED


def test_calculation_requires_firm():
    with pytest.raises(ValueError):
        firm_id(SimpleNamespace(firm_id=None))
