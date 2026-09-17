from typing import Dict, List, Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_agent import CopilotAgent


_AGENTS: Dict[str, CopilotAgent] = {
    "deployment-investigator": CopilotAgent(
        agent_id="deployment-investigator",
        name="Deployment Investigator",
        description=(
            "Investigates deployment status, validation, rollback, "
            "and related operational impact."
        ),
        intents=[
            CopilotIntent.DEPLOYMENT,
            CopilotIntent.EXPLANATION,
            CopilotIntent.CORRELATION,
        ],
        skills=[
            "Deployment Investigation",
            "Operational Explanation",
            "Operational Correlation Review",
        ],
        read_only=True,
        approval_required=False,
    ),
    "incident-investigator": CopilotAgent(
        agent_id="incident-investigator",
        name="Incident Investigator",
        description=(
            "Investigates incidents, severity, priority, and "
            "cross-domain operational context."
        ),
        intents=[
            CopilotIntent.INCIDENT,
            CopilotIntent.EXPLANATION,
            CopilotIntent.CORRELATION,
        ],
        skills=[
            "Incident Investigation",
            "Operational Explanation",
            "Operational Correlation Review",
        ],
        read_only=True,
        approval_required=False,
    ),
    "release-governance": CopilotAgent(
        agent_id="release-governance",
        name="Release Governance Agent",
        description=(
            "Reviews release readiness, governance state, and "
            "related change context."
        ),
        intents=[
            CopilotIntent.RELEASE,
            CopilotIntent.CHANGE,
            CopilotIntent.EXPLANATION,
        ],
        skills=[
            "Release Investigation",
            "Change Investigation",
            "Operational Explanation",
        ],
        read_only=True,
        approval_required=False,
    ),
    "operations-decision": CopilotAgent(
        agent_id="operations-decision",
        name="Operations Decision Agent",
        description=(
            "Synthesizes operational risks, recommendations, and "
            "executive decision context."
        ),
        intents=[
            CopilotIntent.PROJECT_HEALTH,
            CopilotIntent.RECOMMENDATION,
            CopilotIntent.DECISION_BRIEF,
        ],
        skills=[
            "Project Health Review",
            "Recommendation Review",
            "Executive Decision Review",
        ],
        read_only=True,
        approval_required=False,
    ),
}


def get_agent(
    agent_id: str,
) -> Optional[CopilotAgent]:
    return _AGENTS.get(agent_id)


def get_all_agents() -> List[CopilotAgent]:
    return list(_AGENTS.values())


def get_agents_for_intent(
    intent: CopilotIntent,
) -> List[CopilotAgent]:
    return [
        agent
        for agent in _AGENTS.values()
        if intent in agent.intents
    ]
