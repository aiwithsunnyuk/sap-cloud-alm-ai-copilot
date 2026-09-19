from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def _payload(**overrides):
    payload = {
        "decision_id": "DEC-001",
        "decision_status": "success",
        "confidence_score": 100,
        "confidence_level": "high",
        "requested_action": True,
    }
    payload.update(overrides)
    return payload


def test_approval_api_pending_without_human_approval():
    response = client.post(
        "/copilot/approvals/evaluate",
        json=_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision_id"] == "DEC-001"
    assert body["status"] == "pending"
    assert body["allowed_to_proceed"] is False
    assert body["approval_required"] is True


def test_approval_api_allows_explicit_human_approval():
    response = client.post(
        "/copilot/approvals/evaluate",
        json=_payload(
            approver="human-reviewer",
            approval_comment="Approved for controlled execution.",
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "approved"
    assert body["allowed_to_proceed"] is True
    assert body["approval_required"] is True
    assert body["approver"] == "human-reviewer"


def test_approval_api_rejects_blocked_decision():
    response = client.post(
        "/copilot/approvals/evaluate",
        json=_payload(
            decision_status="blocked",
            confidence_score=20,
            confidence_level="low",
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "rejected"
    assert body["allowed_to_proceed"] is False


def test_approval_api_allows_non_action_decision_support():
    response = client.post(
        "/copilot/approvals/evaluate",
        json=_payload(
            requested_action=False,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "approved"
    assert body["allowed_to_proceed"] is True
    assert body["approval_required"] is False


def test_approval_api_rejects_invalid_confidence_score():
    response = client.post(
        "/copilot/approvals/evaluate",
        json=_payload(
            confidence_score=101,
        ),
    )

    assert response.status_code == 422


def test_approval_api_rejects_invalid_confidence_level():
    response = client.post(
        "/copilot/approvals/evaluate",
        json=_payload(
            confidence_level="certain",
        ),
    )

    assert response.status_code == 422
