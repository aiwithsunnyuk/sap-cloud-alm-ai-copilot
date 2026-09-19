from app.models.copilot_decision_assessment import CopilotDecisionAssessment
from app.models.copilot_decision_confidence import (
    CopilotDecisionConfidenceLevel,
)
from app.models.copilot_multi_agent import CopilotMultiAgentDecisionRequest
from app.services.copilot_decision_confidence import (
    calculate_decision_confidence,
)
from app.services.copilot_multi_agent_decision import (
    orchestrate_multi_agent_decision,
)


def assess_multi_agent_decision(
    request: CopilotMultiAgentDecisionRequest,
) -> CopilotDecisionAssessment:
    decision = orchestrate_multi_agent_decision(request)
    confidence = calculate_decision_confidence(decision)

    trace = [
        "Multi-Agent Decision Orchestration",
        "Decision Candidate",
        "Decision Confidence",
        "Decision Assessment",
    ]

    review_required = (
        confidence.level
        in {
            CopilotDecisionConfidenceLevel.LOW,
            CopilotDecisionConfidenceLevel.NONE,
        }
    )

    return CopilotDecisionAssessment(
        decision=decision,
        confidence=confidence,
        auditable=True,
        review_required=review_required,
        trace=trace,
    )
