from typing import Any, Callable, Dict, Optional

from app.models.copilot_tool_result import CopilotToolResult
from app.services.copilot_tool_registry import get_tool


def _project_health() -> Any:
    from app.services.operations_control_tower import (
        get_operations_control_tower,
    )

    return get_operations_control_tower()


def _monitoring_health() -> Any:
    from app.services.monitoring_health import (
        get_monitoring_health,
    )

    return get_monitoring_health()


def _incident_summary() -> Any:
    from app.services.incident_service import (
        get_incident_summary,
    )

    return get_incident_summary()


def _problem_summary() -> Any:
    from app.services.problem_service import (
        get_problem_summary,
    )

    return get_problem_summary()


def _change_summary() -> Any:
    from app.services.change_service import (
        get_change_summary,
    )

    return get_change_summary()


def _release_summary() -> Any:
    from app.services.release_service import (
        get_release_summary,
    )

    return get_release_summary()


def _deployment_summary() -> Any:
    from app.services.deployment_service import (
        get_deployment_summary,
    )

    return get_deployment_summary()


def _correlations() -> Any:
    from app.services.intelligence_correlation import (
        generate_operational_correlations,
    )

    return generate_operational_correlations()


def _explanations() -> Any:
    from app.services.intelligence_explanation import (
        generate_operational_explanations,
    )

    return generate_operational_explanations()


def _recommendations() -> Any:
    from app.services.intelligence_recommendation import (
        generate_operational_recommendations,
    )

    return generate_operational_recommendations()


def _decision_brief() -> Any:
    from app.services.intelligence_decision_brief import (
        generate_operational_decision_brief,
    )

    return generate_operational_decision_brief()


_TRUSTED_DISPATCH: Dict[str, Callable[[], Any]] = {
    "get_project_health": _project_health,
    "get_monitoring_health": _monitoring_health,
    "get_incident_summary": _incident_summary,
    "get_problem_summary": _problem_summary,
    "get_change_summary": _change_summary,
    "get_release_summary": _release_summary,
    "get_deployment_summary": _deployment_summary,
    "get_operational_correlations": _correlations,
    "get_operational_explanations": _explanations,
    "get_operational_recommendations": _recommendations,
    "get_decision_brief": _decision_brief,
}


def execute_tool(
    tool_name: str,
    *,
    approved: bool = False,
) -> CopilotToolResult:
    tool = get_tool(tool_name)

    if tool is None:
        return CopilotToolResult(
            tool_name=tool_name,
            status="blocked",
            source="Tool Registry",
            trace=[
                "Tool Registry",
                "Tool Not Found",
            ],
        )

    if tool.approval_required and not approved:
        return CopilotToolResult(
            tool_name=tool.tool_name,
            status="approval_required",
            source=tool.endpoint,
            trace=[
                "Tool Registry",
                "Governance Check",
                "Approval Required",
            ],
            approval_required=True,
        )

    handler = _TRUSTED_DISPATCH.get(tool.tool_name)

    if handler is None:
        return CopilotToolResult(
            tool_name=tool.tool_name,
            status="blocked",
            source=tool.endpoint,
            trace=[
                "Tool Registry",
                "Trusted Dispatch Check",
                "Tool Not Registered for Execution",
            ],
        )

    try:
        result = handler()

        return CopilotToolResult(
            tool_name=tool.tool_name,
            status="success",
            result=result,
            evidence=[],
            source=tool.endpoint,
            trace=[
                "Tool Registry",
                "Governance Check",
                "Trusted Tool Executor",
                "Trusted Service",
            ],
            approval_required=tool.approval_required,
        )

    except Exception as exc:
        return CopilotToolResult(
            tool_name=tool.tool_name,
            status="error",
            result=None,
            source=tool.endpoint,
            trace=[
                "Tool Registry",
                "Governance Check",
                "Trusted Tool Executor",
                f"Execution Error: {type(exc).__name__}",
            ],
            approval_required=tool.approval_required,
        )
