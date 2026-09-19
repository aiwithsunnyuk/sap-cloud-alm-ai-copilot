from app.models.copilot import CopilotIntent
from app.models.copilot_decision import (
    CopilotAgentContribution,
    CopilotDecisionRequest,
    CopilotDecisionStatus,
)
from app.services.copilot_decision_service import orchestrate_decision


def test_successful_multi_agent_decision_candidate():
    result = orchestrate_decision(
        CopilotDecisionRequest(
            question="Should we review the failed deployment?",
            intent=CopilotIntent.DEPLOYMENT,
            contributions=[
                CopilotAgentContribution(
                    agent_id="deployment-investigator",
                    summary="Deployment rollback detected.",
                    evidence=["DEP-001: rollback completed"],
                    recommendations=[
                        "Review deployment validation evidence."
                    ],
                ),
                CopilotAgentContribution(
                    agent_id="incident-investigator",
                    summary="Related incident identified.",
                    evidence=["INC-003: deployment-related incident"],
                    recommendations=[
                        "Review incident corrective actions."
                    ],
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.SUCCESS
    assert result.decision == "review_recommendations"

    assert result.contributing_agents == [
        "deployment-investigator",
        "incident-investigator",
    ]

    assert len(result.evidence) == 2
    assert len(result.recommendations) == 2

    assert result.action_required is True
    assert result.approval_required is True

    assert result.trace == [
        "Decision Request",
        "Agent Contributions",
        "Evidence Aggregation",
        "Decision Candidate",
    ]


def test_partial_failure_preserves_available_evidence():
    result = orchestrate_decision(
        CopilotDecisionRequest(
            question="Investigate the deployment issue",
            intent=CopilotIntent.DEPLOYMENT,
            contributions=[
                CopilotAgentContribution(
                    agent_id="deployment-investigator",
                    summary="Rollback identified.",
                    evidence=["DEP-001"],
                ),
                CopilotAgentContribution(
                    agent_id="incident-investigator",
                    summary="Incident lookup failed.",
                    status="failed",
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.PARTIAL_FAILURE
    assert result.decision == "review_partial_results"
    assert result.evidence == ["DEP-001"]
    assert result.contributing_agents == [
        "deployment-investigator",
        "incident-investigator",
    ]


def test_blocked_agent_blocks_decision():
    result = orchestrate_decision(
        CopilotDecisionRequest(
            question="Proceed with the deployment?",
            intent=CopilotIntent.DEPLOYMENT,
            contributions=[
                CopilotAgentContribution(
                    agent_id="deployment-investigator",
                    summary="Deployment requires review.",
                    status="blocked",
                    evidence=["DEP-001"],
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.BLOCKED
    assert result.decision == "review_blocked_agents"
    assert result.evidence == ["DEP-001"]
    assert result.action_required is False


def test_no_contributions_is_insufficient_evidence():
    result = orchestrate_decision(
        CopilotDecisionRequest(
            question="What should we review?",
            intent=CopilotIntent.DECISION_BRIEF,
        )
    )

    assert result.status == CopilotDecisionStatus.INSUFFICIENT_EVIDENCE
    assert result.decision == "insufficient_evidence"
    assert result.contributing_agents == []
    assert result.evidence == []
    assert result.recommendations == []
    assert result.action_required is False


def test_unknown_agent_is_recorded_without_inventing_evidence():
    result = orchestrate_decision(
        CopilotDecisionRequest(
            question="Investigate deployment",
            intent=CopilotIntent.DEPLOYMENT,
            contributions=[
                CopilotAgentContribution(
                    agent_id="unknown-agent",
                    summary="Unknown result",
                    evidence=["invented-looking evidence"],
                )
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.PARTIAL_FAILURE
    assert result.decision == "review_partial_results"
    assert result.contributing_agents == []
    assert result.evidence == []
    assert "Unknown agent: unknown-agent" in result.findings


def test_duplicate_evidence_and_recommendations_are_deduplicated():
    result = orchestrate_decision(
        CopilotDecisionRequest(
            question="Review deployment and incident evidence",
            intent=CopilotIntent.DEPLOYMENT,
            contributions=[
                CopilotAgentContribution(
                    agent_id="deployment-investigator",
                    summary="Deployment finding",
                    evidence=["DEP-001"],
                    recommendations=["Review rollback"],
                ),
                CopilotAgentContribution(
                    agent_id="incident-investigator",
                    summary="Incident finding",
                    evidence=["DEP-001"],
                    recommendations=["Review rollback"],
                ),
            ],
        )
    )

    assert result.status == CopilotDecisionStatus.SUCCESS
    assert result.evidence == ["DEP-001"]
    assert result.recommendations == ["Review rollback"]
