from app.models.copilot import CopilotIntent
from app.models.copilot_decision import (
    CopilotDecisionResult,
    CopilotDecisionStatus,
)
from app.services.copilot_decision_confidence import (
    calculate_decision_confidence,
)


def _decision(
    *,
    status=CopilotDecisionStatus.SUCCESS,
    agents=None,
    evidence=None,
    recommendations=None,
):
    return CopilotDecisionResult(
        question="What should we review?",
        intent=CopilotIntent.DEPLOYMENT,
        status=status,
        decision="review_recommendations",
        rationale="Test decision candidate.",
        contributing_agents=agents or [],
        findings=[],
        evidence=evidence or [],
        recommendations=recommendations or [],
        action_required=bool(recommendations),
        approval_required=bool(recommendations),
        trace=["Decision Candidate"],
    )


def test_high_confidence_multi_agent_decision():
    result = calculate_decision_confidence(
        _decision(
            agents=[
                "deployment-investigator",
                "incident-investigator",
            ],
            evidence=[
                "DEP-001",
                "INC-003",
                "PRB-001",
            ],
            recommendations=[
                "Review rollback",
                "Review corrective actions",
            ],
        )
    )

    assert result.score == 100
    assert result.level.value == "high"
    assert result.contributing_agents == 2
    assert result.evidence_items == 3
    assert result.recommendations == 2


def test_successful_single_agent_has_medium_confidence():
    result = calculate_decision_confidence(
        _decision(
            agents=["deployment-investigator"],
            evidence=["DEP-001"],
            recommendations=["Review validation"],
        )
    )

    assert result.score == 70
    assert result.level.value == "medium"


def test_partial_failure_lowers_confidence():
    result = calculate_decision_confidence(
        _decision(
            status=CopilotDecisionStatus.PARTIAL_FAILURE,
            agents=["deployment-investigator"],
            evidence=["DEP-001"],
        )
    )

    assert result.score == 45
    assert result.level.value == "low"


def test_blocked_decision_has_low_confidence():
    result = calculate_decision_confidence(
        _decision(
            status=CopilotDecisionStatus.BLOCKED,
            agents=["deployment-investigator"],
            evidence=["DEP-001"],
        )
    )

    assert result.score == 20
    assert result.level.value == "low"


def test_insufficient_evidence_has_no_confidence():
    result = calculate_decision_confidence(
        _decision(
            status=CopilotDecisionStatus.INSUFFICIENT_EVIDENCE,
        )
    )

    assert result.score == 0
    assert result.level.value == "none"
    assert result.contributing_agents == 0
    assert result.evidence_items == 0


def test_confidence_score_is_capped_at_100():
    result = calculate_decision_confidence(
        _decision(
            agents=[
                "deployment-investigator",
                "incident-investigator",
                "release-governance",
            ],
            evidence=[
                "DEP-001",
                "INC-003",
                "PRB-001",
                "CHG-001",
            ],
            recommendations=[
                "Review rollback",
                "Review incident",
                "Review release",
            ],
        )
    )

    assert result.score == 100
    assert result.level.value == "high"
    assert result.score <= 100
