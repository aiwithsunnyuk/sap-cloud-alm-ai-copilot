from app.models.copilot import CopilotIntent
from app.models.copilot_multi_agent import (
    CopilotAgentOrchestrationInput,
    CopilotMultiAgentDecisionRequest,
)
from app.models.copilot_normalized_result import CopilotNormalizedResult
from app.models.copilot_orchestration import CopilotOrchestrationResult
from app.models.copilot_decision import CopilotDecisionStatus
from app.services.copilot_multi_agent_decision import (
    orchestrate_multi_agent_decision,
)


def _orchestration(
    skill_name: str,
    *,
    status: str = "success",
    evidence=None,
    recommendations=None,
    findings=None,
    successful_tools: int = 1,
    blocked_tools: int = 0,
    failed_tools: int = 0,
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
            "findings": findings or [],
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


def test_multiple_agents_produce_one_decision_candidate():
    result = orchestrate_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="What should we review before the deployment?",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=_orchestration(
                        "Deployment Investigation",
                        evidence=["DEP-001: rollback completed"],
                        findings=["Deployment validation failed."],
                        recommendations=[
                            "Review deployment validation evidence."
                        ],
                    ),
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="incident-investigator",
                    orchestration=_orchestration(
                        "Incident Investigation",
                        evidence=["INC-003: deployment-related incident"],
                        findings=["Related incident remains open."],
                        recommendations=[
                            "Review incident corrective actions."
                        ],
                    ),
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="release-governance",
                    orchestration=_orchestration(
                        "Release Investigation",
                        evidence=["REL-001: planned production release"],
                        findings=["Release requires governance review."],
                        recommendations=[
                            "Review release readiness."
                        ],
                    ),
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.SUCCESS
    assert result.decision == "review_recommendations"

    assert result.contributing_agents == [
        "deployment-investigator",
        "incident-investigator",
        "release-governance",
    ]

    assert len(result.evidence) == 3
    assert len(result.findings) == 3
    assert len(result.recommendations) == 3

    assert result.action_required is True
    assert result.approval_required is True

    assert result.trace[0] == "Multi-Agent Decision Orchestration"
    assert result.trace[-1] == "Decision Candidate"


def test_failed_agent_does_not_destroy_available_evidence():
    result = orchestrate_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Investigate deployment impact",
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

    assert result.status == CopilotDecisionStatus.PARTIAL_FAILURE
    assert result.decision == "review_partial_results"
    assert result.evidence == ["DEP-001"]


def test_blocked_agent_blocks_multi_agent_decision():
    result = orchestrate_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Can we proceed with the deployment?",
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
                CopilotAgentOrchestrationInput(
                    agent_id="release-governance",
                    orchestration=_orchestration(
                        "Release Investigation",
                        evidence=["REL-001"],
                    ),
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.BLOCKED
    assert result.decision == "review_blocked_agents"
    assert result.evidence == ["DEP-001", "REL-001"]


def test_unknown_agent_is_not_added_to_contributing_agents():
    result = orchestrate_multi_agent_decision(
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

    assert result.status == CopilotDecisionStatus.PARTIAL_FAILURE
    assert result.contributing_agents == []
    assert result.evidence == []
    assert "Unknown agent: unknown-agent" in result.findings[0]


def test_empty_multi_agent_request_returns_insufficient_evidence():
    result = orchestrate_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="What should we review?",
            intent=CopilotIntent.DECISION_BRIEF,
            agent_results=[],
        )
    )

    assert result.status == CopilotDecisionStatus.INSUFFICIENT_EVIDENCE
    assert result.decision == "insufficient_evidence"
    assert result.contributing_agents == []
    assert result.evidence == []


def test_duplicate_evidence_across_agents_is_deduplicated():
    result = orchestrate_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Correlate the operational issue",
            intent=CopilotIntent.CORRELATION,
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
                        evidence=["INC-003", "PRB-001"],
                        recommendations=["Review rollback"],
                    ),
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.SUCCESS
    assert result.evidence == [
        "DEP-001",
        "INC-003",
        "PRB-001",
    ]
    assert result.recommendations == ["Review rollback"]
