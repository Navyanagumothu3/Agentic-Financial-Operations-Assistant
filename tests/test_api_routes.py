from fastapi.testclient import TestClient

from api.routes import app


client = TestClient(app)


def test_operate_endpoint_returns_case_result():
    response = client.post(
        "/operate",
        json={
            "customer_id": "C1001",
            "account_id": "A2001",
            "request_type": "refund",
            "amount": 7500,
            "description": "duplicate charge",
            "channel": "chat",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"]
    assert payload["decision"] in {"approve", "resolve", "escalate"}
    assert "approval_required" in payload


def test_cases_endpoint_lists_recent_workflows():
    response = client.get("/cases")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
