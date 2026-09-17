from typing import Dict, List, Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_tool import CopilotTool


_TOOLS: Dict[str, CopilotTool] = {
    "get_project_health": CopilotTool(
        tool_name="get_project_health",
        description="Retrieve overall delivery and operational control-tower health.",
        intent=CopilotIntent.PROJECT_HEALTH,
        endpoint="/operations/control-tower",
        service_function="app.services.operations_control_tower.get_operations_control_tower",
        supported_entity_types=["project", "workstream"],
    ),
    "get_monitoring_health": CopilotTool(
        tool_name="get_monitoring_health",
        description="Retrieve monitoring health, active alerts, and operational status.",
        intent=CopilotIntent.MONITORING,
        endpoint="/monitoring/health",
        service_function="app.services.monitoring_health.get_monitoring_health",
        supported_entity_types=["alert", "monitoring_event"],
    ),
    "get_incident_summary": CopilotTool(
        tool_name="get_incident_summary",
        description="Retrieve incident status, severity, priority, and operational impact.",
        intent=CopilotIntent.INCIDENT,
        endpoint="/incidents",
        service_function="app.services.incident_service.get_incidents",
        supported_entity_types=["incident"],
    ),
    "get_problem_summary": CopilotTool(
        tool_name="get_problem_summary",
        description="Retrieve problem investigation and root-cause information.",
        intent=CopilotIntent.PROBLEM,
        endpoint="/problems",
        service_function="app.services.problem_service.get_problems",
        supported_entity_types=["problem", "incident"],
    ),
    "get_change_summary": CopilotTool(
        tool_name="get_change_summary",
        description="Retrieve change assessment, approval, and implementation information.",
        intent=CopilotIntent.CHANGE,
        endpoint="/changes",
        service_function="app.services.change_service.get_changes",
        supported_entity_types=["change", "problem", "incident"],
    ),
    "get_release_summary": CopilotTool(
        tool_name="get_release_summary",
        description="Retrieve release state and governance information.",
        intent=CopilotIntent.RELEASE,
        endpoint="/releases",
        service_function="app.services.release_service.get_releases",
        supported_entity_types=["release", "change"],
    ),
    "get_deployment_summary": CopilotTool(
        tool_name="get_deployment_summary",
        description="Retrieve deployment status, validation, and rollback information.",
        intent=CopilotIntent.DEPLOYMENT,
        endpoint="/deployments/summary",
        service_function="app.services.deployment_service.get_deployment_summary",
        supported_entity_types=["deployment", "release", "change"],
    ),
    "get_operational_correlations": CopilotTool(
        tool_name="get_operational_correlations",
        description="Retrieve cross-domain operational relationships.",
        intent=CopilotIntent.CORRELATION,
        endpoint="/intelligence/correlations",
        service_function="app.services.intelligence_correlation.get_operational_correlations",
        supported_entity_types=[
            "monitoring_event",
            "incident",
            "problem",
            "change",
            "release",
            "deployment",
        ],
    ),
    "get_operational_explanations": CopilotTool(
        tool_name="get_operational_explanations",
        description="Retrieve evidence-backed operational explanations.",
        intent=CopilotIntent.EXPLANATION,
        endpoint="/intelligence/explanations",
        service_function="app.services.intelligence_explanation.get_operational_explanations",
        supported_entity_types=[
            "incident",
            "problem",
            "change",
            "release",
            "deployment",
        ],
    ),
    "get_operational_recommendations": CopilotTool(
        tool_name="get_operational_recommendations",
        description="Retrieve prioritized operational recommendations.",
        intent=CopilotIntent.RECOMMENDATION,
        endpoint="/intelligence/recommendations",
        service_function="app.services.intelligence_recommendation.generate_operational_recommendations",
        supported_entity_types=[
            "incident",
            "problem",
            "change",
            "release",
            "deployment",
        ],
    ),
    "get_decision_brief": CopilotTool(
        tool_name="get_decision_brief",
        description="Retrieve the consolidated executive operational decision brief.",
        intent=CopilotIntent.DECISION_BRIEF,
        endpoint="/intelligence/decision-brief",
        service_function="app.services.intelligence_decision_brief.generate_operational_decision_brief",
        supported_entity_types=["project", "workstream", "incident", "release"],
    ),
}


def get_tool(
    tool_name: str,
) -> Optional[CopilotTool]:
    return _TOOLS.get(tool_name)


def get_all_tools() -> List[CopilotTool]:
    return list(_TOOLS.values())


def get_tools_for_intent(
    intent: CopilotIntent,
) -> List[CopilotTool]:
    return [
        tool
        for tool in _TOOLS.values()
        if tool.intent == intent
    ]
