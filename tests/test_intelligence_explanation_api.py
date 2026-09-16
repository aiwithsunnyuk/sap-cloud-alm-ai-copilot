from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_operational_explanations_api():
    response = client.get("/intelligence/explanations")

    assert response.status_code == 200

    body = response.json()

    assert body["overall_status"] == "Critical"
    assert body["total_explanations"] > 0
    assert body["critical_explanations"] > 0
    assert body["explanations"]

    explanation = body["explanations"][0]

    assert explanation["what_happened"]
    assert explanation["why_it_matters"]
    assert explanation["operational_impact"]
    assert explanation["evidence"]
    assert explanation["recommended_review"]
