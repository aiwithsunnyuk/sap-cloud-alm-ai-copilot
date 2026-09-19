from app.models.copilot import CopilotIntent
from app.models.copilot_agent_evaluation import (
    CopilotAgentEvaluationStatus,
    CopilotAgentEvaluationRequest,
)
from app.services.copilot_agent_evaluation import evaluate_agent_execution


def _base_request(**overrides):
    payload = {
        "agent_id": "deployment-investigator",
        "intent": CopilotIntent.DEPLOYMENT,
        "trace": [
            "Agent Selection",
            "Skill Planning",
            "Governance",
            "Tool Execution",
            "Handoff",
        ],
    }
    payload.update(overrides)
    return CopilotAgentEvaluationRequest(**payload)


def test_successful_agent_execution_passes():
    result = evaluate_agent_execution(_base_request())

    assert result.status == CopilotAgentEvaluationStatus.PASS
    assert result.score == 100
    assert result.governance_compliant is True
    assert result.skill_plan_valid is True
    assert result.handoff_valid is True
    assert result.execution_successful is True
    assert result.grounded is True
    assert result.trace_complete is True
    assert result.findings == []
    assert result.trace[-1] == "Evaluation"


def test_incomplete_trace_produces_warning():
    result = evaluate_agent_execution(
        _base_request(
            trace=[
                "Agent Selection",
                "Skill Planning",
                "Governance",
                "Tool Execution",
            ]
        )
    )

    assert result.status == CopilotAgentEvaluationStatus.WARN
    assert result.score == 90
    assert result.trace_complete is False
    assert any("trace is incomplete" in item for item in result.findings)


def test_failed_execution_and_ungrounded_response_fail():
    result = evaluate_agent_execution(
        _base_request(
            execution_successful=False,
            grounded=False,
        )
    )

    assert result.status == CopilotAgentEvaluationStatus.FAIL
    assert result.score == 75
    assert result.execution_successful is False
    assert result.grounded is False
    assert len(result.findings) == 2


def test_unknown_agent_fails_safely():
    result = evaluate_agent_execution(
        _base_request(
            agent_id="unknown-agent",
        )
    )

    assert result.status == CopilotAgentEvaluationStatus.FAIL
    assert result.score == 0
    assert result.governance_compliant is False
    assert result.skill_plan_valid is False
    assert result.handoff_valid is False
    assert result.execution_successful is False
    assert result.grounded is False
    assert result.trace_complete is False
    assert result.findings == ["Unknown agent: unknown-agent"]


def test_unapproved_action_can_still_be_governance_compliant():
    result = evaluate_agent_execution(
        _base_request(
            requested_action=True,
            approved=False,
        )
    )

    assert result.governance_compliant is True
    assert result.status == CopilotAgentEvaluationStatus.PASS
    assert result.score == 100
