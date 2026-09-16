from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_risk_history_endpoint():
    response = client.get("/api/v1/tasks/TASK-006/risk-history")

    assert response.status_code == 200

    body = response.json()

    assert body["task_id"] == "TASK-006"
    assert len(body["snapshots"]) == 5
    assert body["snapshots"][0]["risk_score"] == 58
    assert body["snapshots"][-1]["risk_score"] == 100


def test_risk_trend_endpoint():
    response = client.get("/api/v1/tasks/TASK-006/risk-trend")

    assert response.status_code == 200

    body = response.json()

    assert body["task_id"] == "TASK-006"
    assert body["risk_change"] == 42
    assert body["risk_velocity"] == 10.5
    assert body["trend"] == "Deteriorating"
    assert body["severity_transition"] == "High → Critical"


def test_risk_trend_unknown_task():
    response = client.get("/api/v1/tasks/TASK-999/risk-trend")

    assert response.status_code == 404
