from app.models.copilot import CopilotIntent
from app.models.copilot_decision import (
    CopilotDecisionResult,
    CopilotDecisionStatus,
)
from app.models.copilot_decision_assessment import (
    CopilotDecisionAssessment,
)
from app.models.copilot_decision_confidence import (
    CopilotDecisionConfidence,
    CopilotDecisionConfidenceLevel,
)
from app.services.copilot_approval_audit import clear_approval_audit
from app.services.copilot_decision_approval import (
    evaluate_decision_approval,
)


def setup_function():
    clear_approval_audit()


def _assessment(
    *,
    status=CopilotDecisionStatus.SUCCESS,
    confidence_score=100,
    confidence_level=CopilotDecisionConfidenceLevel.HIGH,
    action_required=True,
):
    decision = CopilotDecisionResult(
        question="Should the deployment proceed?",
        intent=CopilotIntent.DEPLOYMENT,
        status=status,
        decision="review_recommendations",
        rationale="Test decision assessment.",
        contributing_agents=[
            "deployment-investigator",
            "incident-investigator",
        ],
        findings=["Deployment validation requires review."],
        evidence=[
            "DEP-001",
            "INC-003",
            "PRB-001",
        ],
        recommendations=[
            "Review deployment validation."
        ],
        action_required=action_required,
        approval_required=action_required,
        trace=["Decision Candidate"],
    )

    confidence = CopilotDecisionConfidence(
        score=confidence_score,
        level=confidence_level,
        decision_status=status,
        contributing_agents=2,
        evidence_items=3,
        recommendations=1,
        rationale="Test confidence.",
    )

    return CopilotDecisionAssessment(
        decision=decision,
        confidence=confidence,
        auditable=True,
        review_required=False,
        trace=[
            "Multi-Agent Decision Orchestration",
            "Decision Candidate",
            "Decision Confidence",
            "Decision Assessment",
        ],
    )


def test_action_decision_without_human_approval_is_pending_and_audited():
    result = evaluate_decision_approval(
        "DEC-001",
        _assessment(),
    )

    assert result.decision_id == "DEC-001"

    assert result.approval.status.value == "pending"
    assert result.allowed_to_proceed is False

    assert result.audit_record.audit_id == "AUD-001"
    assert result.audit_record.decision_id == "DEC-001"
    assert result.audit_record.status.value == "pending"


def test_explicit_human_approval_is_linked_to_decision_and_audit():
    result = evaluate_decision_approval(
        "DEC-002",
        _assessment(),
        approver="human-reviewer",
        approval_comment="Approved for controlled execution.",
    )

    assert result.approval.status.value == "approved"
    assert result.allowed_to_proceed is True

    assert result.approval.approver == "human-reviewer"
    assert result.approval.approval_comment == (
        "Approved for controlled execution."
    )

    assert result.audit_record.decision_id == "DEC-002"
    assert result.audit_record.status.value == "approved"
    assert result.audit_record.allowed_to_proceed is True


def test_rejection_is_linked_without_allowing_execution():
    result = evaluate_decision_approval(
        "DEC-003",
        _assessment(),
        approver="human-reviewer",
        approval_comment="Rejected pending additional evidence.",
    )

    assert result.approval.status.value == "rejected"
    assert result.allowed_to_proceed is False

    assert result.audit_record.decision_id == "DEC-003"
    assert result.audit_record.status.value == "rejected"


def test_non_action_decision_support_does_not_create_action_gate():
    result = evaluate_decision_approval(
        "DEC-004",
        _assessment(
            action_required=False,
            confidence_score=70,
            confidence_level=CopilotDecisionConfidenceLevel.MEDIUM,
        ),
    )

    assert result.approval.status.value == "approved"
    assert result.approval.approval_required is False
    assert result.allowed_to_proceed is True

    assert result.audit_record.decision_id == "DEC-004"
    assert result.audit_record.approval_required is False


def test_low_confidence_action_remains_pending():
    result = evaluate_decision_approval(
        "DEC-005",
        _assessment(
            confidence_score=20,
            confidence_level=CopilotDecisionConfidenceLevel.LOW,
        ),
    )

    assert result.approval.status.value == "pending"
    assert result.allowed_to_proceed is False

    assert result.audit_record.decision_id == "DEC-005"
    assert result.audit_record.status.value == "pending"


def test_blocked_decision_is_rejected_and_audited():
    result = evaluate_decision_approval(
        "DEC-006",
        _assessment(
            status=CopilotDecisionStatus.BLOCKED,
            confidence_score=20,
            confidence_level=CopilotDecisionConfidenceLevel.LOW,
        ),
    )

    assert result.approval.status.value == "rejected"
    assert result.allowed_to_proceed is False

    assert result.audit_record.decision_id == "DEC-006"


def test_trace_shows_decision_to_approval_to_audit():
    result = evaluate_decision_approval(
        "DEC-007",
        _assessment(),
    )

    assert result.trace[0] == "Decision Assessment"
    assert "Decision → Approval Link" in result.trace
    assert "Approval Audit" in result.trace
