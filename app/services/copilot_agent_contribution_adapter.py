from app.models.copilot_decision import CopilotAgentContribution
from app.models.copilot_orchestration import CopilotOrchestrationResult
from app.services.copilot_agent_registry import get_agent


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)

    return result


def _extract_list(data, key: str) -> list[str]:
    if not isinstance(data, dict):
        return []

    value = data.get(key)

    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, str) and item
    ]


def _extract_recommendation_actions(data) -> list[str]:
    actions: list[str] = []

    def add(value) -> None:
        if isinstance(value, str) and value and value not in actions:
            actions.append(value)

    def extract_items(items, fields) -> None:
        if not isinstance(items, list):
            return

        for item in items:
            # Preserve legacy/simple list payloads.
            if isinstance(item, str):
                add(item)
                continue

            if not isinstance(item, dict):
                continue

            for field in fields:
                value = item.get(field)

                if isinstance(value, str) and value:
                    add(value)
                    break

    if not isinstance(data, dict):
        return actions

    # Recommendation service contract.
    extract_items(
        data.get("recommendations"),
        ("action", "recommendation", "recommended_action"),
    )

    # Correlation service contract.
    extract_items(
        data.get("correlations"),
        ("recommended_action",),
    )

    # Direct recommended_action remains supported.
    direct_action = data.get("recommended_action")
    if isinstance(direct_action, str) and direct_action:
        add(direct_action)

    return actions



def build_agent_contribution(
    agent_id: str,
    orchestration: CopilotOrchestrationResult,
) -> CopilotAgentContribution:
    agent = get_agent(agent_id)

    if agent is None:
        return CopilotAgentContribution(
            agent_id=agent_id,
            summary=f"Unknown agent: {agent_id}",
            status="failed",
        )

    findings: list[str] = []
    evidence: list[str] = []
    recommendations: list[str] = []

    for tool_result in orchestration.tool_results:
        evidence.extend(tool_result.evidence)

        findings.extend(
            _extract_list(tool_result.data, "findings")
        )

        recommendations.extend(
            _extract_recommendation_actions(tool_result.data)
        )

    evidence = _unique(evidence)
    findings = _unique(findings)
    recommendations = _unique(recommendations)

    if orchestration.failed_tools > 0:
        status = "failed"
    elif orchestration.blocked_tools > 0:
        status = "blocked"
    else:
        status = "success"

    summary = (
        f"{agent.name} executed skill "
        f"'{orchestration.skill_name}' with status "
        f"'{orchestration.status}'."
    )

    if orchestration.failed_tools > 0:
        summary += (
            f" {orchestration.failed_tools} tool(s) failed."
        )
    elif orchestration.blocked_tools > 0:
        summary += (
            f" {orchestration.blocked_tools} tool(s) were blocked."
        )

    return CopilotAgentContribution(
        agent_id=agent.agent_id,
        summary=summary,
        status=status,
        findings=findings,
        evidence=evidence,
        recommendations=recommendations,
    )
