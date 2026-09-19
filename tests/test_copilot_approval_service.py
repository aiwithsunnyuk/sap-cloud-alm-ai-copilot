from app.models.copilot_approval import (
    CopilotApprovalRequest,
    CopilotApprovalStatus,
)
from app.models.copilot_decision import CopilotDecisionStatus
from app.models.copilot_decision_confidence import (
    CopilotDecisionConfidenceLevel,
)
from app.services.copilot_approval_service import evaluate_approval


def _request(**overrides):
    payload = {
        "decision_id": "DEC-001",
        "decision_status": CopilotDecisionStatus.SUCCESS,
        "confidence_score": 100,
        "confidence_level": CopilotDecisionConfidenceLevel.HIGH,
        "requested_action": True,
    }

    payload.update(overrides)

    return CopilotApprovalRequest(**payload)


def test_non_action_decision_support_does_not_require_approval():
    result = evaluate_approval(
        _request(
            requested_action=False,
        )
    )

    assert result.status == CopilotApprovalStatus.APPROVED
    assert result.allowed_to_proceed is True
    assert result.approval_required is False


def test_action_without_approver_remains_pending():
    result = evaluate_approval(_request())

    assert result.status == CopilotApprovalStatus.PENDING
    assert result.allowed_to_proceed is False
    assert result.approval_required is True


def test_low_confidence_action_requires_human_review():
    result = evaluate_approval(
        _request(
            confidence_score=20,
            confidence_level=CopilotDecisionConfidenceLevel.LOW,
        )
    )

    assert result.status == CopilotApprovalStatus.PENDING
    assert result.allowed_to_proceed is False
    assert result.approval_required is True


def test_insufficient_evidence_action_is_rejected():
    result = evaluate_approval(
        _request(
            decision_status=CopilotDecisionStatus.INSUFFICIENT_EVIDENCE,
            confidence_score=0,
            confidence_level=CopilotDecisionConfidenceLevel.NONE,
        )
    )

    assert result.status == CopilotApprovalStatus.REJECTED
    assert result.allowed_to_proceed is False
    assert result.approval_required is True


def test_blocked_action_is_rejected():
    result = evaluate_approval(
        _request(
            decision_status=CopilotDecisionStatus.BLOCKED,
            confidence_score=20,
            confidence_level=CopilotDecisionConfidenceLevel.LOW,
        )
    )

    assert result.status == CopilotApprovalStatus.REJECTED
    assert result.allowed_to_proceed is False


def test_explicit_human_approval_allows_action():
    result = evaluate_approval(
        _request(
            approver="human-reviewer",
            approval_comment="Approved for controlled execution.",
        )
    )

    assert result.status == CopilotApprovalStatus.APPROVED
    assert result.allowed_to_proceed is True
    assert result.approval_required is True
    assert result.approver == "human-reviewer"


def test_explicit_non_approval_blocks_action():
    result = evaluate_approval(
        _request(
            approver="human-reviewer",
            approval_comment="Rejected pending additional evidence.",
        )
    )

    assert result.status == CopilotApprovalStatus.REJECTED
    assert result.allowed_to_proceed is False
    assert result.approver == "human-reviewer"
