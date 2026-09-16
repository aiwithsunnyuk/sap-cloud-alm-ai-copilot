from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.models.copilot import CopilotIntent, CopilotQueryRequest
from app.models.copilot_response import CopilotResponse
from app.services.copilot_router import classify_copilot_query
from app.services.deployment_service import get_deployment_summary
from app.services.incident_service import get_incident_summary
from app.services.intelligence_correlation import generate_operational_correlations
from app.services.intelligence_decision_brief import (
    generate_operational_decision_brief,
)
from app.services.intelligence_explanation import (
    generate_operational_explanations,
)
from app.services.intelligence_recommendation import (
    generate_operational_recommendations,
)
from app.services.intelligence_service import generate_operational_intelligence
from app.services.monitoring_health import calculate_monitoring_health
from app.services.operations_control_tower import calculate_operations_control_tower
from app.services.problem_service import get_problem_summary
from app.services.change_service import get_change_summary
from app.services.release_service import get_release_summary


def _value(source: Any, name: str, default: Any = None) -> Any:
    if source is None:
        return default

    if isinstance(source, dict):
        return source.get(name, default)

    return getattr(source, name, default)


def _items(source: Any, name: str) -> list[Any]:
    value = _value(source, name, [])

    if value is None:
        return []

    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        return list(value)

    return [value]


def _format_status(value: Any) -> str:
    if value is None:
        return "Unknown"
    return str(value)


def _control_tower_response() -> tuple[str, list[str], list[str], bool]:
    result = calculate_operations_control_tower()

    status = _format_status(_value(result, "overall_status"))

    monitoring = _value(result, "monitoring", {}) or {}
    incidents = _value(result, "incidents", {}) or {}
    problems = _value(result, "problems", {}) or {}
    changes = _value(result, "changes", {}) or {}
    releases = _value(result, "releases", {}) or {}
    deployments = _value(result, "deployments", {}) or {}

    evidence = [
        f"Active alerts: {_value(monitoring, 'active_alerts', 0)}",
        f"Open incidents: {_value(incidents, 'open_incidents', 0)}",
        f"Active problems: {_value(problems, 'active_problems', 0)}",
        f"Pending approvals: {_value(changes, 'pending_approval', 0)}",
        f"Active releases: {_value(releases, 'active_releases', 0)}",
        f"Rolled-back deployments: "
        f"{_value(deployments, 'rolled_back_deployments', 0)}",
        f"Failed validations: "
        f"{_value(deployments, 'failed_validations', 0)}",
    ]

    actions = _items(result, "executive_actions")

    answer = (
        f"The current operational status is {status}. "
        f"The control tower reports "
        f"{_value(monitoring, 'active_alerts', 0)} active alert(s), "
        f"{_value(incidents, 'open_incidents', 0)} open incident(s), "
        f"{_value(problems, 'active_problems', 0)} active problem(s), "
        f"and {_value(changes, 'pending_approval', 0)} pending approval(s)."
    )

    if actions:
        answer += f" Immediate review focus: {actions[0]}"

    return answer, evidence, ["Control Tower"], True


def _monitoring_response() -> tuple[str, list[str], list[str], bool]:
    result = calculate_monitoring_health()

    status = _format_status(_value(result, "overall_status"))
    score = _value(result, "health_score", 0)

    evidence = [
        f"Monitoring status: {status}",
        f"Health score: {score}",
        f"Total events: {_value(result, 'total_events', 0)}",
        f"Active events: {_value(result, 'active_events', 0)}",
        f"Active alerts: {_value(result, 'active_alerts', 0)}",
        f"Critical alerts: {_value(result, 'critical_alerts', 0)}",
        f"High alerts: {_value(result, 'high_alerts', 0)}",
    ]

    answer = (
        f"Monitoring is currently {status} with a health score of {score}. "
        f"There are {_value(result, 'active_alerts', 0)} active alert(s), "
        f"including {_value(result, 'critical_alerts', 0)} critical "
        f"and {_value(result, 'high_alerts', 0)} high-severity alert(s)."
    )

    return answer, evidence, ["Monitoring Health"], True


def _incident_response() -> tuple[str, list[str], list[str], bool]:
    result = get_incident_summary()

    open_incidents = _value(result, "open_incidents", 0)
    critical = _value(result, "critical_incidents", 0)
    high = _value(result, "high_incidents", 0)

    evidence = [
        f"Open incidents: {open_incidents}",
        f"Critical incidents: {critical}",
        f"High incidents: {high}",
    ]

    answer = (
        f"There are {open_incidents} open incident(s), including "
        f"{critical} critical and {high} high-severity incident(s)."
    )

    return answer, evidence, ["Incident Management"], True


def _problem_response() -> tuple[str, list[str], list[str], bool]:
    result = get_problem_summary()

    active = _value(result, "active_problems", 0)
    unresolved = _value(result, "unresolved_root_causes", 0)
    rca_identified = _value(result, "rca_identified", 0)

    evidence = [
        f"Active problems: {active}",
        f"RCA identified: {rca_identified}",
        f"Unresolved root causes: {unresolved}",
    ]

    answer = (
        f"There are {active} active problem(s). "
        f"{rca_identified} have an identified root cause, while "
        f"{unresolved} remain unresolved."
    )

    return answer, evidence, ["Problem Management"], unresolved > 0


def _change_response() -> tuple[str, list[str], list[str], bool]:
    result = get_change_summary()

    active = _value(result, "active_changes", 0)
    pending = _value(result, "pending_approval", 0)

    evidence = [
        f"Active changes: {active}",
        f"Pending approvals: {pending}",
    ]

    answer = (
        f"There are {active} active change request(s), with "
        f"{pending} currently awaiting approval."
    )

    return answer, evidence, ["Change Management"], pending > 0


def _release_response() -> tuple[str, list[str], list[str], bool]:
    result = get_release_summary()

    total = _value(result, "total_releases", _value(result, "total", 0))
    active = _value(result, "active_releases", 0)
    planned = _value(result, "planned_releases", 0)
    ready = _value(result, "ready_releases", 0)
    completed = _value(result, "completed_releases", 0)

    evidence = [
        f"Total releases: {total}",
        f"Active releases: {active}",
        f"Planned releases: {planned}",
        f"Ready releases: {ready}",
        f"Completed releases: {completed}",
    ]

    answer = (
        f"There are {total} release(s), with {active} active. "
        f"The current lifecycle includes {planned} planned, "
        f"{ready} ready, and {completed} completed release(s)."
    )

    return answer, evidence, ["Release Management"], active > 0


def _deployment_response() -> tuple[str, list[str], list[str], bool]:
    result = get_deployment_summary()

    rolled_back = _value(result, "rolled_back_deployments", 0)
    failed = _value(result, "failed_validations", 0)

    evidence = [
        f"Rolled-back deployments: {rolled_back}",
        f"Failed validations: {failed}",
    ]

    answer = (
        f"Deployment status includes {rolled_back} rolled-back deployment(s) "
        f"and {failed} failed validation(s)."
    )

    if rolled_back > 0:
        answer += (
            " Rollback evidence should be reviewed before repeating "
            "the affected deployment activity."
        )

    return answer, evidence, ["Deployment Management"], rolled_back > 0 or failed > 0


def _intelligence_response() -> tuple[str, list[str], list[str], bool]:
    result = generate_operational_intelligence()

    insights = _items(result, "insights")
    critical = _value(result, "critical_insights", 0)
    high = _value(result, "high_insights", 0)

    evidence = [
        f"Total insights: {_value(result, 'total_insights', len(insights))}",
        f"Critical insights: {critical}",
        f"High insights: {high}",
    ]

    for insight in insights[:3]:
        title = _value(insight, "title", "Operational insight")
        evidence.append(f"Insight: {title}")

    answer = (
        f"The intelligence layer has {_value(result, 'total_insights', len(insights))} "
        f"active insight(s), including {critical} critical and {high} high."
    )

    return answer, evidence, ["Operational Intelligence"], bool(insights)


def _correlation_response() -> tuple[str, list[str], list[str], bool]:
    result = generate_operational_correlations()

    correlations = _items(result, "correlations")

    evidence = [
        f"Total correlations: "
        f"{_value(result, 'total_correlations', len(correlations))}",
    ]

    trace = ["Cross-Domain Correlations"]

    if correlations:
        correlation = correlations[0]
        chain = _items(correlation, "causal_chain")

        if chain:
            evidence.append(
                "Causal chain: " + " → ".join(str(item) for item in chain)
            )
            trace.append(" → ".join(str(item) for item in chain))

        answer = (
            "The intelligence layer identified a traceable operational chain: "
            f"{' → '.join(str(item) for item in chain)}."
            if chain
            else "A cross-domain operational correlation was identified."
        )
    else:
        answer = "No cross-domain operational correlations were identified."

    return answer, evidence, trace, bool(correlations)


def _explanation_response() -> tuple[str, list[str], list[str], bool]:
    result = generate_operational_explanations()

    explanations = _items(result, "explanations")

    evidence = [
        f"Total explanations: "
        f"{_value(result, 'total_explanations', len(explanations))}",
    ]

    if not explanations:
        return (
            "No operational explanations are currently available.",
            evidence,
            ["Explainability"],
            False,
        )

    explanation = explanations[0]

    for field in (
        "what_happened",
        "why_it_matters",
        "operational_impact",
    ):
        value = _value(explanation, field)
        if value:
            evidence.append(f"{field.replace('_', ' ').title()}: {value}")

    answer = _value(
        explanation,
        "why_it_matters",
        "An operational explanation is available for review.",
    )

    return answer, evidence, ["Explainability"], True


def _recommendation_response() -> tuple[str, list[str], list[str], bool, bool]:
    result = generate_operational_recommendations()

    recommendations = _items(result, "recommendations")
    total = _value(result, "total_recommendations", len(recommendations))
    p1 = _value(result, "p1_recommendations", 0)
    p2 = _value(result, "p2_recommendations", 0)

    evidence = [
        f"Total recommendations: {total}",
        f"P1 recommendations: {p1}",
        f"P2 recommendations: {p2}",
    ]

    answer = (
        f"There are {total} prioritized recommendation(s), including "
        f"{p1} P1 and {p2} P2 item(s)."
    )

    if recommendations:
        top = recommendations[0]
        action = _value(top, "action")
        if action:
            answer += f" Highest-priority action: {action}"
            evidence.append(f"Top action: {action}")

    return answer, evidence, ["Recommendations"], p1 > 0, True


def _decision_brief_response() -> tuple[str, list[str], list[str], bool]:
    result = generate_operational_decision_brief()

    status = _format_status(_value(result, "overall_status"))
    total_risks = _value(result, "total_risks", 0)
    priority_actions = _value(result, "priority_actions_count", 0)
    summary = _value(result, "executive_summary")

    evidence = [
        f"Overall status: {status}",
        f"Total risks: {total_risks}",
        f"Priority actions: {priority_actions}",
    ]

    answer = summary or (
        f"The current decision brief status is {status}, with "
        f"{total_risks} risk(s) and {priority_actions} priority action(s)."
    )

    return answer, evidence, ["Decision Brief"], True


def generate_copilot_response(
    request: CopilotQueryRequest,
) -> CopilotResponse:
    route = classify_copilot_query(request)

    if route.intent == CopilotIntent.UNKNOWN:
        return CopilotResponse(
            question=request.question,
            intent=route.intent,
            confidence=route.confidence,
            answer=(
                "I could not map this question to a trusted operational "
                "capability. Please ask about delivery health, monitoring, "
                "incidents, problems, changes, releases, deployments, "
                "correlations, explanations, recommendations, or the "
                "executive decision brief."
            ),
            evidence=[],
            source_capability=route.target_capability,
            source_endpoint=route.suggested_endpoint,
            trace=["Intent Router", "No trusted capability"],
            grounded=False,
            action_required=False,
            approval_required=False,
        )

    action_required = False
    approval_required = False

    if route.intent == CopilotIntent.PROJECT_HEALTH:
        answer, evidence, trace, action_required = _control_tower_response()
    elif route.intent == CopilotIntent.MONITORING:
        answer, evidence, trace, action_required = _monitoring_response()
    elif route.intent == CopilotIntent.INCIDENT:
        answer, evidence, trace, action_required = _incident_response()
    elif route.intent == CopilotIntent.PROBLEM:
        answer, evidence, trace, action_required = _problem_response()
    elif route.intent == CopilotIntent.CHANGE:
        answer, evidence, trace, action_required = _change_response()
    elif route.intent == CopilotIntent.RELEASE:
        answer, evidence, trace, action_required = _release_response()
    elif route.intent == CopilotIntent.DEPLOYMENT:
        answer, evidence, trace, action_required = _deployment_response()
    elif route.intent == CopilotIntent.CORRELATION:
        answer, evidence, trace, action_required = _correlation_response()
    elif route.intent == CopilotIntent.EXPLANATION:
        answer, evidence, trace, action_required = _explanation_response()
    elif route.intent == CopilotIntent.RECOMMENDATION:
        (
            answer,
            evidence,
            trace,
            action_required,
            approval_required,
        ) = _recommendation_response()
    elif route.intent == CopilotIntent.DECISION_BRIEF:
        answer, evidence, trace, action_required = _decision_brief_response()
    else:
        answer, evidence, trace, action_required = _intelligence_response()

    return CopilotResponse(
        question=request.question,
        intent=route.intent,
        confidence=route.confidence,
        answer=answer,
        evidence=evidence,
        source_capability=route.target_capability,
        source_endpoint=route.suggested_endpoint,
        trace=["Intent Router", *trace],
        grounded=True,
        action_required=action_required,
        approval_required=approval_required,
    )
