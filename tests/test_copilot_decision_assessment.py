from app.models.copilot import CopilotIntent
from app.models.copilot_decision import CopilotDecisionStatus
from app.models.copilot_multi_agent import (
    CopilotAgentOrchestrationInput,
    CopilotMultiAgentDecisionRequest,
)
from app.models.copilot_normalized_result import CopilotNormalizedResult
from app.models.copilot_orchestration import CopilotOrchestrationResult
from app.services.copilot_decision_assessment import (
    assess_multi_agent_decision,
)


def _orchestration(
    skill_name: str,
    *,
    evidence=None,
    recommendations=None,
    status="success",
    successful_tools=1,
    blocked_tools=0,
    failed_tools=0,
):
    tool_name = {
        "Deployment Investigation": "get_deployment_summary",
        "Incident Investigation": "get_incident_summary",
        "Release Investigation": "get_release_summary",
    }.get(skill_name, "get_project_health")

    normalized = CopilotNormalizedResult(
        tool_name=tool_name,
        status="success",
        summary=f"{skill_name} result",
        data={
            "findings": [],
            "recommendations": recommendations or [],
        },
        evidence=evidence or [],
        source=f"{skill_name} service",
        trace=["Tool Execution"],
        approval_required=False,
    )

    return CopilotOrchestrationResult(
        skill_name=skill_name,
        intent=CopilotIntent.DEPLOYMENT,
        status=status,
        tool_results=[normalized],
        successful_tools=successful_tools,
        blocked_tools=blocked_tools,
        failed_tools=failed_tools,
        approval_required=False,
        trace=[
            "Skill Planning",
            "Tool Execution",
            "Normalized Tool Results",
        ],
    )


def test_successful_multi_agent_assessment_is_high_quality():
    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="What should we review before deployment?",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=_orchestration(
                        "Deployment Investigation",
                        evidence=["DEP-001", "INC-003"],
                        recommendations=["Review rollback"],
                    ),
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="incident-investigator",
                    orchestration=_orchestration(
                        "Incident Investigation",
                        evidence=["PRB-001"],
                        recommendations=[
                            "Review corrective actions"
                        ],
                    ),
                ),
            ],
        )
    )

    assert result.auditable is True
    assert result.review_required is False

    assert result.decision.status == CopilotDecisionStatus.SUCCESS
    assert result.confidence.score == 100
    assert result.confidence.level.value == "high"

    assert result.trace == [
        "Multi-Agent Decision Orchestration",
        "Decision Candidate",
        "Decision Confidence",
        "Decision Assessment",
    ]


def test_single_agent_assessment_is_reviewable_when_confidence_is_medium():
    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Review deployment",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=_orchestration(
                        "Deployment Investigation",
                        evidence=["DEP-001"],
                        recommendations=["Review validation"],
                    ),
                ),
            ],
        )
    )

    assert result.decision.status == CopilotDecisionStatus.SUCCESS
    assert result.confidence.score == 70
    assert result.confidence.level.value == "medium"
    assert result.review_required is False


def test_partial_failure_requires_review():
    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Investigate deployment",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=_orchestration(
                        "Deployment Investigation",
                        evidence=["DEP-001"],
                    ),
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="incident-investigator",
                    orchestration=_orchestration(
                        "Incident Investigation",
                        status="partial_failure",
                        failed_tools=1,
                        successful_tools=0,
                    ),
                ),
            ],
        )
    )

    assert result.decision.status == CopilotDecisionStatus.PARTIAL_FAILURE
    assert result.confidence.score == 55
    assert result.confidence.level.value == "medium"
    assert result.review_required is False


def test_blocked_decision_requires_review():
    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Can deployment proceed?",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=_orchestration(
                        "Deployment Investigation",
                        status="partially_blocked",
                        blocked_tools=1,
                        successful_tools=0,
                        evidence=["DEP-001"],
                    ),
                ),
            ],
        )
    )

    assert result.decision.status == CopilotDecisionStatus.BLOCKED
    assert result.confidence.score == 20
    assert result.confidence.level.value == "low"
    assert result.review_required is True


def test_empty_assessment_has_no_confidence_and_requires_review():
    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="What should we review?",
            intent=CopilotIntent.DECISION_BRIEF,
            agent_results=[],
        )
    )

    assert (
        result.decision.status
        == CopilotDecisionStatus.INSUFFICIENT_EVIDENCE
    )
    assert result.confidence.score == 0
    assert result.confidence.level.value == "none"
    assert result.review_required is True
    assert result.auditable is True


def test_unknown_agent_produces_failed_assessment_without_evidence():
    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Investigate deployment",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="unknown-agent",
                    orchestration=_orchestration(
                        "Deployment Investigation",
                        evidence=["should-not-be-trusted"],
                    ),
                ),
            ],
        )
    )

    assert result.decision.status == CopilotDecisionStatus.PARTIAL_FAILURE
    assert result.decision.evidence == []
    assert result.confidence.score == 45
    assert result.confidence.level.value == "low"
    assert result.review_required is True
