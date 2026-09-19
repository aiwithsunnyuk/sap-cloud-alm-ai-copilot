from app.models.copilot_agent_evaluation import (
    CopilotAgentEvaluation,
    CopilotAgentEvaluationRequest,
    CopilotAgentEvaluationStatus,
)
from app.services.copilot_agent_governance import evaluate_agent_governance
from app.services.copilot_agent_registry import get_agent


_REQUIRED_TRACE_STEPS = {
    "Agent Selection",
    "Skill Planning",
    "Governance",
    "Tool Execution",
    "Handoff",
}


def _governance_is_compliant(
    request: CopilotAgentEvaluationRequest,
    agent,
    governance,
) -> bool:
    if governance.allowed:
        return True

    # A read-only agent must refuse operational actions.
    if request.requested_action and getattr(agent, "read_only", False):
        return True

    # An action that requires approval is correctly blocked until approval exists.
    if governance.approval_required and not request.approved:
        return True

    return False


def evaluate_agent_execution(
    request: CopilotAgentEvaluationRequest,
) -> CopilotAgentEvaluation:
    trace = list(request.trace)
    findings: list[str] = []

    agent = get_agent(request.agent_id)

    if agent is None:
        trace.append("Evaluation")
        return CopilotAgentEvaluation(
            agent_id=request.agent_id,
            intent=request.intent,
            status=CopilotAgentEvaluationStatus.FAIL,
            score=0,
            governance_compliant=False,
            skill_plan_valid=False,
            handoff_valid=False,
            execution_successful=False,
            grounded=False,
            trace_complete=False,
            findings=[f"Unknown agent: {request.agent_id}"],
            trace=trace,
        )

    governance = evaluate_agent_governance(
        agent_id=request.agent_id,
        requested_action=request.requested_action,
        approved=request.approved,
    )

    governance_compliant = _governance_is_compliant(
        request=request,
        agent=agent,
        governance=governance,
    )

    if not governance_compliant:
        findings.append("Agent governance policy was not satisfied.")

    if not request.skill_plan_valid:
        findings.append("Skill plan validation failed.")

    if not request.handoff_valid:
        findings.append("Agent handoff validation failed.")

    if not request.execution_successful:
        findings.append("Agent/tool execution did not complete successfully.")

    if not request.grounded:
        findings.append("Agent response was not grounded in trusted evidence.")

    trace_complete = _REQUIRED_TRACE_STEPS.issubset(set(trace))

    if not trace_complete:
        missing = sorted(_REQUIRED_TRACE_STEPS - set(trace))
        findings.append(
            "Execution trace is incomplete. Missing: "
            + ", ".join(missing)
        )

    score = 100

    if not governance_compliant:
        score -= 30

    if not request.skill_plan_valid:
        score -= 20

    if not request.handoff_valid:
        score -= 15

    if not request.execution_successful:
        score -= 15

    if not request.grounded:
        score -= 10

    if not trace_complete:
        score -= 10

    score = max(0, score)

    critical_failure = (
        not governance_compliant
        or not request.execution_successful
    )

    if critical_failure or score < 70:
        status = CopilotAgentEvaluationStatus.FAIL
    elif score >= 90 and not findings:
        status = CopilotAgentEvaluationStatus.PASS
    else:
        status = CopilotAgentEvaluationStatus.WARN

    trace.append("Evaluation")

    return CopilotAgentEvaluation(
        agent_id=request.agent_id,
        intent=request.intent,
        status=status,
        score=score,
        governance_compliant=governance_compliant,
        skill_plan_valid=request.skill_plan_valid,
        handoff_valid=request.handoff_valid,
        execution_successful=request.execution_successful,
        grounded=request.grounded,
        trace_complete=trace_complete,
        findings=findings,
        trace=trace,
    )
