from app.models.copilot_decision import (
    CopilotDecisionRequest,
    CopilotDecisionResult,
)
from app.models.copilot_multi_agent import (
    CopilotAgentOrchestrationInput,
    CopilotMultiAgentDecisionRequest,
)
from app.services.copilot_agent_contribution_adapter import (
    build_agent_contribution,
)
from app.services.copilot_decision_service import orchestrate_decision


def orchestrate_multi_agent_decision(
    request: CopilotMultiAgentDecisionRequest,
) -> CopilotDecisionResult:
    contributions = []

    for agent_result in request.agent_results:
        contribution = build_agent_contribution(
            agent_id=agent_result.agent_id,
            orchestration=agent_result.orchestration,
        )
        contributions.append(contribution)

    decision_request = CopilotDecisionRequest(
        question=request.question,
        intent=request.intent,
        contributions=contributions,
    )

    result = orchestrate_decision(decision_request)

    # Preserve the multi-agent layer explicitly in the execution trace.
    trace = [
        "Multi-Agent Decision Orchestration",
        *result.trace,
    ]

    result.trace = trace

    return result
