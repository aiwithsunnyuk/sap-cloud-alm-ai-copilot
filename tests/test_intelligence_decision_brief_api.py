from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_operational_decision_brief_api():
    response = client.get("/intelligence/decision-brief")

    assert response.status_code == 200

    body = response.json()

    assert body["brief_id"] == "BRIEF-001"
    assert body["overall_status"] == "Critical"
    assert body["total_risks"] > 0
    assert body["priority_actions_count"] > 0
    assert body["top_risks"]
    assert body["priority_actions"]
    assert body["decision_points"]
    assert body["evidence"]
