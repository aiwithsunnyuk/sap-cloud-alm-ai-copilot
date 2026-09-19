from app.models.copilot_decision import CopilotDecisionResult
from app.models.copilot_decision_confidence import (
    CopilotDecisionConfidence,
    CopilotDecisionConfidenceLevel,
)


_BASE_SCORES = {
    "success": 70,
    "partial_failure": 45,
    "blocked": 20,
    "insufficient_evidence": 0,
}


def calculate_decision_confidence(
    decision: CopilotDecisionResult,
) -> CopilotDecisionConfidence:
    score = _BASE_SCORES[decision.status.value]

    agents = len(decision.contributing_agents)
    evidence = len(decision.evidence)
    recommendations = len(decision.recommendations)

    bonuses: list[str] = []

    # Insufficient evidence is an explicit zero-confidence state.
    # No structural bonus can override the absence of evidence.
    if decision.status.value != "insufficient_evidence":
        if agents >= 2:
            score += 10
            bonuses.append("multiple contributing agents")

        if evidence >= 3:
            score += 10
            bonuses.append("three or more evidence items")

        if recommendations >= 2:
            score += 10
            bonuses.append("multiple recommendations")

    score = min(100, score)

    if score >= 80:
        level = CopilotDecisionConfidenceLevel.HIGH
    elif score >= 50:
        level = CopilotDecisionConfidenceLevel.MEDIUM
    elif score > 0:
        level = CopilotDecisionConfidenceLevel.LOW
    else:
        level = CopilotDecisionConfidenceLevel.NONE

    if score == 0:
        rationale = (
            "No reliable confidence can be assigned because the decision "
            "candidate lacks sufficient evidence."
        )
    elif bonuses:
        rationale = (
            f"Support confidence is {score} based on the decision status "
            f"plus {', '.join(bonuses)}."
        )
    else:
        rationale = (
            f"Support confidence is {score} based primarily on the "
            f"decision status and available evidence."
        )

    return CopilotDecisionConfidence(
        score=score,
        level=level,
        decision_status=decision.status,
        contributing_agents=agents,
        evidence_items=evidence,
        recommendations=recommendations,
        rationale=rationale,
    )
