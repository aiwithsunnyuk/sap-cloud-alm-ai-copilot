from app.models.copilot_approval import CopilotApprovalRequest
from app.models.copilot_decision_approval import CopilotDecisionApprovalResult
from app.models.copilot_decision_assessment import CopilotDecisionAssessment
from app.services.copilot_approval_audit import record_approval_audit
from app.services.copilot_approval_service import evaluate_approval


def evaluate_decision_approval(
    decision_id: str,
    assessment: CopilotDecisionAssessment,
    approver: str | None = None,
    approval_comment: str | None = None,
) -> CopilotDecisionApprovalResult:
    decision = assessment.decision
    confidence = assessment.confidence

    approval_request = CopilotApprovalRequest(
        decision_id=decision_id,
        decision_status=decision.status,
        confidence_score=confidence.score,
        confidence_level=confidence.level,
        requested_action=decision.action_required,
        approver=approver,
        approval_comment=approval_comment,
    )

    approval = evaluate_approval(approval_request)
    audit_record = record_approval_audit(approval)

    trace = [
        "Decision Assessment",
        "Decision → Approval Link",
        *approval.trace,
        "Approval Audit",
    ]

    return CopilotDecisionApprovalResult(
        decision_id=decision_id,
        assessment=assessment,
        approval=approval,
        audit_record=audit_record,
        allowed_to_proceed=approval.allowed_to_proceed,
        trace=trace,
    )
