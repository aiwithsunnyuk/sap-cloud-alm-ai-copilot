from fastapi.testclient import TestClient

from app.api import app
from app.models.copilot_approval import (
    CopilotApprovalResult,
    CopilotApprovalStatus,
)
from app.services.copilot_approval_audit import clear_approval_audit
from app.services.copilot_approval_audit import record_approval_audit


client = TestClient(app)


def setup_function():
    clear_approval_audit()


def _record(
    *,
    decision_id="DEC-001",
    status=CopilotApprovalStatus.PENDING,
    allowed_to_proceed=False,
    approval_required=True,
    approver=None,
    approval_comment=None,
):
    return record_approval_audit(
        CopilotApprovalResult(
            decision_id=decision_id,
            status=status,
            allowed_to_proceed=allowed_to_proceed,
            approval_required=approval_required,
            approver=approver,
            approval_comment=approval_comment,
            rationale="Test approval audit result.",
            trace=[
                "Approval Request",
                "Approval Policy Evaluation",
            ],
        )
    )


def test_audit_api_returns_records():
    _record()

    response = client.get("/copilot/approvals/audit")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["audit_id"] == "AUD-001"
    assert body[0]["decision_id"] == "DEC-001"
    assert body[0]["status"] == "pending"


def test_audit_summary_api_returns_counts():
    _record(decision_id="DEC-001")

    _record(
        decision_id="DEC-002",
        status=CopilotApprovalStatus.APPROVED,
        allowed_to_proceed=True,
    )

    _record(
        decision_id="DEC-003",
        status=CopilotApprovalStatus.REJECTED,
    )

    response = client.get(
        "/copilot/approvals/audit/summary"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_records"] == 3
    assert body["pending"] == 1
    assert body["approved"] == 1
    assert body["rejected"] == 1


def test_audit_detail_api_returns_specific_record():
    record = _record(
        decision_id="DEC-010",
        status=CopilotApprovalStatus.APPROVED,
        allowed_to_proceed=True,
        approver="human-reviewer",
        approval_comment="Approved for controlled execution.",
    )

    response = client.get(
        f"/copilot/approvals/audit/{record.audit_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["audit_id"] == "AUD-001"
    assert body["decision_id"] == "DEC-010"
    assert body["status"] == "approved"
    assert body["allowed_to_proceed"] is True
    assert body["approver"] == "human-reviewer"


def test_audit_detail_api_returns_404_for_unknown_record():
    response = client.get(
        "/copilot/approvals/audit/AUD-999"
    )

    assert response.status_code == 404


def test_empty_audit_api_returns_empty_list():
    response = client.get("/copilot/approvals/audit")

    assert response.status_code == 200
    assert response.json() == []


def test_empty_audit_summary_returns_zero_counts():
    response = client.get(
        "/copilot/approvals/audit/summary"
    )

    assert response.status_code == 200

    body = response.json()

    assert body == {
        "total_records": 0,
        "pending": 0,
        "approved": 0,
        "rejected": 0,
    }
