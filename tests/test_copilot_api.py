from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_copilot_query_deployment_rollback():
    response = client.post(
        "/copilot/query",
        json={"question": "Why was the deployment rolled back?"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["intent"] == "deployment"
    assert body["grounded"] is True
    assert body["action_required"] is True
    assert body["approval_required"] is False
    assert body["evidence"]
    assert body["answer"]


def test_copilot_query_unknown_is_safe():
    response = client.post(
        "/copilot/query",
        json={"question": "What should I have for lunch today?"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["intent"] == "unknown"
    assert body["grounded"] is False
    assert body["evidence"] == []
    assert body["answer"]
