from typing import Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_agent_skill_plan import (
    CopilotAgentSkillPlan,
)
from app.services.copilot_agent_registry import get_agent
from app.services.copilot_skill_planner import build_skill_plan


def build_agent_skill_plan(
    agent_id: str,
    intent: CopilotIntent,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> Optional[CopilotAgentSkillPlan]:
    agent = get_agent(agent_id)

    if agent is None:
        return None

    if intent not in agent.intents:
        return None

    skill_plan = build_skill_plan(
        intent,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    if skill_plan is None:
        return None

    if skill_plan.skill_name not in agent.skills:
        return None

    return CopilotAgentSkillPlan(
        agent_id=agent.agent_id,
        agent_name=agent.name,
        intent=intent,
        skill=skill_plan,
        rationale=(
            f"{agent.name} owns the '{skill_plan.skill_name}' "
            f"skill for the {intent.value} intent."
        ),
        trace=[
            "Agent Selection",
            "Agent Skill Planner",
        ],
    )
