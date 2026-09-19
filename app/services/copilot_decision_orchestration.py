from app.models.copilot_decision_response import (
    CopilotDecisionOrchestrationResponse,
)
from app.models.copilot_multi_agent import (
    CopilotMultiAgentDecisionRequest,
)
from app.services.copilot_decision_confidence import (
    calculate_decision_confidence,
)
from app.services.copilot_multi_agent_decision import (
    orchestrate_multi_agent_decision,
)


def orchestrate_decision_with_confidence(
    request: CopilotMultiAgentDecisionRequest,
) -> CopilotDecisionOrchestrationResponse:
    decision = orchestrate_multi_agent_decision(request)

    confidence = calculate_decision_confidence(decision)

    decision.trace.append("Decision Confidence")

    return CopilotDecisionOrchestrationResponse(
        decision=decision,
        confidence=confidence,
    )
