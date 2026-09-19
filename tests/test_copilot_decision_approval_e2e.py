from app.models.copilot import CopilotIntent
from app.models.copilot_multi_agent import (
    CopilotAgentOrchestrationInput,
    CopilotMultiAgentDecisionRequest,
)
from app.services.copilot_approval_audit import (
    clear_approval_audit,
    get_approval_audit_summary,
)
from app.services.copilot_decision_approval import (
    evaluate_decision_approval,
)
from app.services.copilot_decision_assessment import (
    assess_multi_agent_decision,
)
from app.services.copilot_orchestrator import orchestrate_skill


def setup_function():
    clear_approval_audit()


def _build_real_assessment():
    deployment_result = orchestrate_skill(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    incident_result = orchestrate_skill(
        CopilotIntent.INCIDENT,
        entity_type="incident",
        entity_id="INC-003",
    )

    release_result = orchestrate_skill(
        CopilotIntent.RELEASE,
        entity_type="release",
        entity_id="REL-001",
    )

    assert deployment_result is not None
    assert incident_result is not None
    assert release_result is not None

    return assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question=(
                "What should we review before proceeding "
                "with the deployment?"
            ),
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=deployment_result,
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="incident-investigator",
                    orchestration=incident_result,
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="release-governance",
                    orchestration=release_result,
                ),
            ],
        )
    )


def test_real_decision_to_pending_approval_to_audit():
    assessment = _build_real_assessment()

    assert assessment.auditable is True
    assert assessment.decision.action_required is True
    assert assessment.confidence.score >= 80

    result = evaluate_decision_approval(
        decision_id="DEC-E2E-001",
        assessment=assessment,
    )

    assert result.decision_id == "DEC-E2E-001"

    assert result.approval.status.value == "pending"
    assert result.approval.allowed_to_proceed is False
    assert result.approval.approval_required is True

    assert result.audit_record.audit_id == "AUD-001"
    assert result.audit_record.decision_id == "DEC-E2E-001"
    assert result.audit_record.status.value == "pending"
    assert result.audit_record.allowed_to_proceed is False


def test_real_decision_to_human_approval_to_audit():
    assessment = _build_real_assessment()

    result = evaluate_decision_approval(
        decision_id="DEC-E2E-002",
        assessment=assessment,
        approver="human-reviewer",
        approval_comment="Approved for controlled execution.",
    )

    assert result.approval.status.value == "approved"
    assert result.approval.allowed_to_proceed is True
    assert result.approval.approver == "human-reviewer"

    assert result.audit_record.audit_id == "AUD-001"
    assert result.audit_record.decision_id == "DEC-E2E-002"
    assert result.audit_record.status.value == "approved"
    assert result.audit_record.allowed_to_proceed is True


def test_real_decision_to_human_rejection_to_audit():
    assessment = _build_real_assessment()

    result = evaluate_decision_approval(
        decision_id="DEC-E2E-003",
        assessment=assessment,
        approver="human-reviewer",
        approval_comment="Rejected pending additional evidence.",
    )

    assert result.approval.status.value == "rejected"
    assert result.approval.allowed_to_proceed is False

    assert result.audit_record.audit_id == "AUD-001"
    assert result.audit_record.decision_id == "DEC-E2E-003"
    assert result.audit_record.status.value == "rejected"


def test_multiple_human_decisions_create_distinct_audit_records():
    assessment = _build_real_assessment()

    first = evaluate_decision_approval(
        decision_id="DEC-E2E-004",
        assessment=assessment,
    )

    second = evaluate_decision_approval(
        decision_id="DEC-E2E-005",
        assessment=assessment,
        approver="human-reviewer",
        approval_comment="Approved for controlled execution.",
    )

    assert first.audit_record.audit_id == "AUD-001"
    assert second.audit_record.audit_id == "AUD-002"

    summary = get_approval_audit_summary()

    assert summary.total_records == 2
    assert summary.pending == 1
    assert summary.approved == 1
    assert summary.rejected == 0


def test_rejected_human_decision_never_allows_execution():
    assessment = _build_real_assessment()

    result = evaluate_decision_approval(
        decision_id="DEC-E2E-006",
        assessment=assessment,
        approver="human-reviewer",
        approval_comment="Rejected.",
    )

    assert result.allowed_to_proceed is False
    assert result.approval.status.value == "rejected"
    assert result.audit_record.allowed_to_proceed is False

    assert "Approval Audit" in result.trace
