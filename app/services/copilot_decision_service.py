from app.models.copilot_decision import (
    CopilotAgentContribution,
    CopilotDecisionRequest,
    CopilotDecisionResult,
    CopilotDecisionStatus,
)
from app.services.copilot_agent_registry import get_agent


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def orchestrate_decision(
    request: CopilotDecisionRequest,
) -> CopilotDecisionResult:
    trace = [
        "Decision Request",
        "Agent Contributions",
    ]

    findings: list[str] = []
    evidence: list[str] = []
    recommendations: list[str] = []
    contributing_agents: list[str] = []

    if not request.contributions:
        trace.append("Evidence Aggregation")
        trace.append("Decision Candidate")

        return CopilotDecisionResult(
            question=request.question,
            intent=request.intent,
            status=CopilotDecisionStatus.INSUFFICIENT_EVIDENCE,
            decision="insufficient_evidence",
            rationale="No agent contributions were provided.",
            trace=trace,
        )

    failed = 0
    blocked = 0

    for contribution in request.contributions:
        agent = get_agent(contribution.agent_id)

        if agent is None:
            findings.append(
                f"Unknown agent: {contribution.agent_id}"
            )
            failed += 1
            continue

        contributing_agents.append(contribution.agent_id)

        findings.extend(contribution.findings)
        evidence.extend(contribution.evidence)
        recommendations.extend(contribution.recommendations)

        status = contribution.status.lower()

        if status == "blocked":
            blocked += 1
        elif status != "success":
            failed += 1

    trace.append("Evidence Aggregation")

    findings = _unique(findings)
    evidence = _unique(evidence)
    recommendations = _unique(recommendations)
    contributing_agents = _unique(contributing_agents)

    if blocked > 0:
        status = CopilotDecisionStatus.BLOCKED
        decision = "review_blocked_agents"
        rationale = (
            f"{blocked} agent contribution(s) are blocked. "
            "Decision review cannot proceed without resolving the "
            "blocked contribution(s)."
        )
    elif failed > 0:
        status = CopilotDecisionStatus.PARTIAL_FAILURE
        decision = "review_partial_results"
        rationale = (
            f"{failed} agent contribution(s) failed or were unavailable. "
            "The decision candidate is based only on available evidence."
        )
    elif not evidence:
        status = CopilotDecisionStatus.INSUFFICIENT_EVIDENCE
        decision = "insufficient_evidence"
        rationale = (
            "Agent contributions were received, but no evidence was "
            "provided to support a decision."
        )
    else:
        status = CopilotDecisionStatus.SUCCESS
        decision = "review_recommendations"
        rationale = (
            f"Decision candidate aggregated from "
            f"{len(contributing_agents)} agent contribution(s) "
            f"and {len(evidence)} evidence item(s)."
        )

    action_required = bool(recommendations)

    # M14 produces a decision candidate only.
    # Approval/execution belongs to later governance milestones.
    approval_required = action_required

    trace.append("Decision Candidate")

    return CopilotDecisionResult(
        question=request.question,
        intent=request.intent,
        status=status,
        decision=decision,
        rationale=rationale,
        contributing_agents=contributing_agents,
        findings=findings,
        evidence=evidence,
        recommendations=recommendations,
        action_required=action_required,
        approval_required=approval_required,
        trace=trace,
    )
