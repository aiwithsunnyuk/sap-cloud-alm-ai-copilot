from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_operational_recommendations_api():
    response = client.get("/intelligence/recommendations")

    assert response.status_code == 200

    body = response.json()

    assert body["overall_status"] == "Critical"
    assert body["total_recommendations"] == 4
    assert body["p1_recommendations"] == 2
    assert body["p2_recommendations"] == 1
    assert body["recommendations"]

    scores = [
        item["priority_score"]
        for item in body["recommendations"]
    ]

    assert scores == sorted(scores, reverse=True)
