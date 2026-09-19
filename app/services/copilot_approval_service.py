from app.models.copilot_approval import (
    CopilotApprovalRequest,
    CopilotApprovalResult,
    CopilotApprovalStatus,
)
from app.models.copilot_decision import CopilotDecisionStatus
from app.models.copilot_decision_confidence import (
    CopilotDecisionConfidenceLevel,
)


def evaluate_approval(
    request: CopilotApprovalRequest,
) -> CopilotApprovalResult:
    trace = [
        "Approval Request",
        "Approval Policy Evaluation",
    ]

    # A decision that does not require an action can proceed as
    # decision-support output without an approval gate.
    if not request.requested_action:
        trace.append("Approval Not Required")

        return CopilotApprovalResult(
            decision_id=request.decision_id,
            status=CopilotApprovalStatus.APPROVED,
            allowed_to_proceed=True,
            approval_required=False,
            approver=request.approver,
            approval_comment=request.approval_comment,
            rationale=(
                "No operational action was requested. "
                "The decision remains decision-support output."
            ),
            trace=trace,
        )

    # Any blocked or insufficient-evidence decision cannot proceed.
    if request.decision_status in {
        CopilotDecisionStatus.BLOCKED,
        CopilotDecisionStatus.INSUFFICIENT_EVIDENCE,
    }:
        trace.append("Approval Blocked")
        trace.append("Governance Gate")

        return CopilotApprovalResult(
            decision_id=request.decision_id,
            status=CopilotApprovalStatus.REJECTED,
            allowed_to_proceed=False,
            approval_required=True,
            approver=request.approver,
            approval_comment=request.approval_comment,
            rationale=(
                "The decision cannot proceed because its current "
                "evidence state is blocked or insufficient."
            ),
            trace=trace,
        )

    # Low-confidence action candidates remain pending even when the
    # request itself is otherwise valid.
    if request.confidence_level in {
        CopilotDecisionConfidenceLevel.LOW,
        CopilotDecisionConfidenceLevel.NONE,
    }:
        trace.append("Approval Pending")
        trace.append("Human Review Required")

        return CopilotApprovalResult(
            decision_id=request.decision_id,
            status=CopilotApprovalStatus.PENDING,
            allowed_to_proceed=False,
            approval_required=True,
            approver=request.approver,
            approval_comment=request.approval_comment,
            rationale=(
                "Human review is required because confidence "
                "is below the action approval threshold."
            ),
            trace=trace,
        )

    # An action request with no explicit approver decision stays pending.
    if request.approver is None:
        trace.append("Approval Pending")
        trace.append("Awaiting Human Decision")

        return CopilotApprovalResult(
            decision_id=request.decision_id,
            status=CopilotApprovalStatus.PENDING,
            allowed_to_proceed=False,
            approval_required=True,
            rationale=(
                "An operational action was requested, but no "
                "human approval has been recorded."
            ),
            trace=trace,
        )

    approver_decision = (request.approval_comment or "").strip().lower()

    if approver_decision.startswith("approved"):
        trace.append("Human Approved")
        trace.append("Governance Gate Passed")

        return CopilotApprovalResult(
            decision_id=request.decision_id,
            status=CopilotApprovalStatus.APPROVED,
            allowed_to_proceed=True,
            approval_required=True,
            approver=request.approver,
            approval_comment=request.approval_comment,
            rationale="Human approval was explicitly recorded.",
            trace=trace,
        )

    trace.append("Human Rejected")
    trace.append("Governance Gate Blocked")

    return CopilotApprovalResult(
        decision_id=request.decision_id,
        status=CopilotApprovalStatus.REJECTED,
        allowed_to_proceed=False,
        approval_required=True,
        approver=request.approver,
        approval_comment=request.approval_comment,
        rationale="Human approval was not explicitly granted.",
        trace=trace,
    )
