from typing import Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_skill import CopilotSkillInvocation
from app.models.copilot_skill_plan import CopilotSkillPlan
from app.services.copilot_tool_registry import get_tool


_SKILL_DEFINITIONS = {
    CopilotIntent.PROJECT_HEALTH: {
        "name": "Project Health Review",
        "description": "Review overall delivery and operational health.",
        "tools": ["get_project_health", "get_operational_recommendations"],
    },
    CopilotIntent.MONITORING: {
        "name": "Monitoring Investigation",
        "description": "Review active monitoring health and operational alerts.",
        "tools": ["get_monitoring_health"],
    },
    CopilotIntent.INCIDENT: {
        "name": "Incident Investigation",
        "description": "Review incidents and their operational context.",
        "tools": [
            "get_incident_summary",
            "get_operational_correlations",
            "get_operational_recommendations",
        ],
    },
    CopilotIntent.PROBLEM: {
        "name": "Problem Investigation",
        "description": "Review problem investigation and root-cause context.",
        "tools": [
            "get_problem_summary",
            "get_operational_correlations",
            "get_operational_recommendations",
        ],
    },
    CopilotIntent.CHANGE: {
        "name": "Change Investigation",
        "description": "Review change assessment, approval, and impact.",
        "tools": ["get_change_summary", "get_operational_correlations"],
    },
    CopilotIntent.RELEASE: {
        "name": "Release Investigation",
        "description": "Review release state and governance context.",
        "tools": ["get_release_summary", "get_operational_correlations"],
    },
    CopilotIntent.DEPLOYMENT: {
        "name": "Deployment Investigation",
        "description": (
            "Review deployment status, validation, rollback, "
            "and related operational context."
        ),
        "tools": [
            "get_deployment_summary",
            "get_operational_correlations",
            "get_operational_recommendations",
        ],
    },
    CopilotIntent.CORRELATION: {
        "name": "Operational Correlation Review",
        "description": "Review relationships across operational objects.",
        "tools": ["get_operational_correlations"],
    },
    CopilotIntent.EXPLANATION: {
        "name": "Operational Explanation",
        "description": "Provide evidence-backed operational explanation.",
        "tools": [
            "get_operational_explanations",
            "get_operational_correlations",
        ],
    },
    CopilotIntent.RECOMMENDATION: {
        "name": "Recommendation Review",
        "description": "Review prioritized operational recommendations.",
        "tools": ["get_operational_recommendations"],
    },
    CopilotIntent.DECISION_BRIEF: {
        "name": "Executive Decision Review",
        "description": "Review consolidated risks and priority actions.",
        "tools": [
            "get_decision_brief",
            "get_operational_recommendations",
        ],
    },
}


def build_skill_plan(
    intent: CopilotIntent,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> Optional[CopilotSkillPlan]:
    definition = _SKILL_DEFINITIONS.get(intent)

    if definition is None:
        return None

    invocations = []

    for tool_name in definition["tools"]:
        tool = get_tool(tool_name)

        if tool is None:
            continue

        invocations.append(
            CopilotSkillInvocation(
                intent=tool.intent,
                capability_name=tool.tool_name,
                endpoint=tool.endpoint,
                read_only=tool.read_only,
                approval_required=tool.approval_required,
                entity_type=entity_type,
                entity_id=entity_id,
            )
        )

    if not invocations:
        return None

    return CopilotSkillPlan(
        skill_name=definition["name"],
        description=definition["description"],
        intent=intent,
        tools=invocations,
        primary_tool=invocations[0].capability_name,
        read_only=all(
            invocation.read_only
            for invocation in invocations
        ),
        approval_required=any(
            invocation.approval_required
            for invocation in invocations
        ),
    )
