from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_operational_intelligence_api():
    response = client.get("/intelligence/operational")

    assert response.status_code == 200

    body = response.json()

    assert body["overall_status"] == "Critical"
    assert body["total_insights"] == 6
    assert body["critical_insights"] == 2
    assert body["high_insights"] == 4
    assert len(body["insights"]) == 6
