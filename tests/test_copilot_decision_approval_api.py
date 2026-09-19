from fastapi.testclient import TestClient

from app.api import app
from app.services.copilot_approval_audit import clear_approval_audit


client = TestClient(app)


def setup_function():
    clear_approval_audit()


def _assessment(
    *,
    action_required=True,
    status="success",
    confidence_score=100,
    confidence_level="high",
):
    return {
        "decision": {
            "question": "Should the deployment proceed?",
            "intent": "deployment",
            "status": status,
            "decision": "review_recommendations",
            "rationale": "Synthetic decision assessment.",
            "contributing_agents": [
                "deployment-investigator",
                "incident-investigator",
            ],
            "findings": [
                "Deployment validation requires review."
            ],
            "evidence": [
                "DEP-001",
                "INC-003",
                "PRB-001",
            ],
            "recommendations": [
                "Review deployment validation."
            ],
            "action_required": action_required,
            "approval_required": action_required,
            "trace": [
                "Decision Candidate"
            ],
        },
        "confidence": {
            "score": confidence_score,
            "level": confidence_level,
            "decision_status": status,
            "contributing_agents": 2,
            "evidence_items": 3,
            "recommendations": 1,
            "rationale": "Synthetic confidence assessment.",
        },
        "auditable": True,
        "review_required": False,
        "trace": [
            "Multi-Agent Decision Orchestration",
            "Decision Candidate",
            "Decision Confidence",
            "Decision Assessment",
        ],
    }


def test_decision_approval_api_creates_pending_audit():
    response = client.post(
        "/copilot/decisions/DEC-001/approval",
        json={
            "assessment": _assessment(),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision_id"] == "DEC-001"

    assert body["approval"]["status"] == "pending"
    assert body["approval"]["allowed_to_proceed"] is False
    assert body["approval"]["approval_required"] is True

    assert body["audit_record"]["audit_id"] == "AUD-001"
    assert body["audit_record"]["decision_id"] == "DEC-001"
    assert body["audit_record"]["status"] == "pending"


def test_decision_approval_api_accepts_explicit_human_approval():
    response = client.post(
        "/copilot/decisions/DEC-002/approval",
        json={
            "assessment": _assessment(),
            "approver": "human-reviewer",
            "approval_comment": "Approved for controlled execution.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["approval"]["status"] == "approved"
    assert body["approval"]["allowed_to_proceed"] is True

    assert body["approval"]["approver"] == "human-reviewer"

    assert body["audit_record"]["status"] == "approved"
    assert body["audit_record"]["allowed_to_proceed"] is True


def test_decision_approval_api_rejects_explicit_human_rejection():
    response = client.post(
        "/copilot/decisions/DEC-003/approval",
        json={
            "assessment": _assessment(),
            "approver": "human-reviewer",
            "approval_comment": "Rejected pending additional evidence.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["approval"]["status"] == "rejected"
    assert body["approval"]["allowed_to_proceed"] is False

    assert body["audit_record"]["status"] == "rejected"
    assert body["audit_record"]["allowed_to_proceed"] is False


def test_decision_approval_api_rejects_blocked_decision():
    response = client.post(
        "/copilot/decisions/DEC-004/approval",
        json={
            "assessment": _assessment(
                status="blocked",
                confidence_score=20,
                confidence_level="low",
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["approval"]["status"] == "rejected"
    assert body["approval"]["allowed_to_proceed"] is False


def test_decision_approval_api_allows_non_action_decision_support():
    response = client.post(
        "/copilot/decisions/DEC-005/approval",
        json={
            "assessment": _assessment(
                action_required=False,
                confidence_score=70,
                confidence_level="medium",
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["approval"]["status"] == "approved"
    assert body["approval"]["allowed_to_proceed"] is True
    assert body["approval"]["approval_required"] is False


def test_decision_approval_api_rejects_malformed_assessment():
    response = client.post(
        "/copilot/decisions/DEC-006/approval",
        json={
            "assessment": {
                "auditable": True,
            }
        },
    )

    assert response.status_code == 422
