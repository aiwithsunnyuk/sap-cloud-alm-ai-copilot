from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_operational_correlations_api():
    response = client.get("/intelligence/correlations")

    assert response.status_code == 200

    body = response.json()

    assert body["overall_status"] == "Critical"
    assert body["total_correlations"] > 0
    assert body["critical_correlations"] > 0
    assert body["correlations"]
