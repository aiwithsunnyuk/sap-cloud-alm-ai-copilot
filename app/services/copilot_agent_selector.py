from typing import Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_agent_selection import (
    CopilotAgentSelection,
)
from app.services.copilot_agent_registry import (
    get_agents_for_intent,
)


_ENTITY_AGENT_MAP = {
    "deployment": "deployment-investigator",
    "incident": "incident-investigator",
    "release": "release-governance",
    "change": "release-governance",
    "project": "operations-decision",
    "workstream": "operations-decision",
}


def select_agent(
    intent: CopilotIntent,
    entity_type: Optional[str] = None,
) -> CopilotAgentSelection:
    candidates = get_agents_for_intent(intent)

    candidate_ids = [
        agent.agent_id
        for agent in candidates
    ]

    trace = [
        "Intent Router",
        "Agent Registry",
        "Agent Selection",
    ]

    if not candidates:
        return CopilotAgentSelection(
            intent=intent,
            status="none",
            candidate_agent_ids=[],
            entity_type=entity_type,
            rationale=(
                "No registered specialized agent supports "
                "the requested intent."
            ),
            trace=trace,
        )

    if entity_type:
        normalized_entity = entity_type.strip().lower()
        preferred_agent_id = _ENTITY_AGENT_MAP.get(
            normalized_entity
        )

        if preferred_agent_id:
            for agent in candidates:
                if agent.agent_id == preferred_agent_id:
                    return CopilotAgentSelection(
                        intent=intent,
                        status="selected",
                        selected_agent_id=agent.agent_id,
                        selected_agent_name=agent.name,
                        candidate_agent_ids=candidate_ids,
                        entity_type=entity_type,
                        rationale=(
                            f"Selected {agent.name} because "
                            f"entity type '{entity_type}' maps "
                            "to its registered ownership."
                        ),
                        trace=trace,
                    )

    if len(candidates) == 1:
        agent = candidates[0]

        return CopilotAgentSelection(
            intent=intent,
            status="selected",
            selected_agent_id=agent.agent_id,
            selected_agent_name=agent.name,
            candidate_agent_ids=candidate_ids,
            entity_type=entity_type,
            rationale=(
                f"Selected {agent.name} because it is the "
                "only registered agent for this intent."
            ),
            trace=trace,
        )

    return CopilotAgentSelection(
        intent=intent,
        status="ambiguous",
        selected_agent_id=None,
        selected_agent_name=None,
        candidate_agent_ids=candidate_ids,
        entity_type=entity_type,
        rationale=(
            "Multiple specialized agents support this intent. "
            "Additional entity context is required for "
            "deterministic ownership selection."
        ),
        trace=trace,
    )
