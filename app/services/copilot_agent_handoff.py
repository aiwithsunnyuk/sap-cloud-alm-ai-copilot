from typing import Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_agent_handoff import CopilotAgentHandoff
from app.services.copilot_agent_registry import get_agent
from app.services.copilot_agent_selector import select_agent


_HANDOFF_RULES = {
    "deployment-investigator": {
        CopilotIntent.INCIDENT,
        CopilotIntent.RECOMMENDATION,
        CopilotIntent.DECISION_BRIEF,
    },
    "incident-investigator": {
        CopilotIntent.RECOMMENDATION,
        CopilotIntent.DECISION_BRIEF,
    },
    "release-governance": {
        CopilotIntent.DEPLOYMENT,
        CopilotIntent.RECOMMENDATION,
    },
}


def request_agent_handoff(
    source_agent_id: str,
    target_intent: CopilotIntent,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> CopilotAgentHandoff:
    source_agent = get_agent(source_agent_id)

    trace = [
        "Source Agent",
        "Handoff Rule Check",
        "Target Agent Selection",
    ]

    if source_agent is None:
        return CopilotAgentHandoff(
            source_agent_id=source_agent_id,
            target_intent=target_intent,
            entity_type=entity_type,
            entity_id=entity_id,
            status="blocked",
            reason="Source agent is not registered.",
            trace=trace,
        )

    allowed_intents = _HANDOFF_RULES.get(
        source_agent_id,
        set(),
    )

    if target_intent not in allowed_intents:
        return CopilotAgentHandoff(
            source_agent_id=source_agent_id,
            target_intent=target_intent,
            entity_type=entity_type,
            entity_id=entity_id,
            status="blocked",
            reason=(
                f"{source_agent.name} is not authorized for "
                f"handoff to intent '{target_intent.value}'."
            ),
            trace=trace,
        )

    selection = select_agent(
        target_intent,
        entity_type=entity_type,
    )

    trace.extend(selection.trace)

    if selection.status != "selected":
        return CopilotAgentHandoff(
            source_agent_id=source_agent_id,
            target_intent=target_intent,
            entity_type=entity_type,
            entity_id=entity_id,
            status="unavailable",
            reason=(
                "A deterministic target agent could not be "
                "selected for the requested handoff."
            ),
            trace=trace,
        )

    if selection.selected_agent_id == source_agent_id:
        return CopilotAgentHandoff(
            source_agent_id=source_agent_id,
            target_agent_id=selection.selected_agent_id,
            target_agent_name=selection.selected_agent_name,
            target_intent=target_intent,
            entity_type=entity_type,
            entity_id=entity_id,
            status="blocked",
            reason="Agent handoff cannot target the same agent.",
            trace=trace,
        )

    return CopilotAgentHandoff(
        source_agent_id=source_agent_id,
        target_agent_id=selection.selected_agent_id,
        target_agent_name=selection.selected_agent_name,
        target_intent=target_intent,
        entity_type=entity_type,
        entity_id=entity_id,
        status="allowed",
        reason=(
            f"Handoff from {source_agent.name} to "
            f"{selection.selected_agent_name} is permitted by "
            "the registered handoff rules."
        ),
        approval_required=False,
        trace=trace + ["Handoff Allowed"],
    )
