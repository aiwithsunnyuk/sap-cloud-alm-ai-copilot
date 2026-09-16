from app.services.monitoring_health import calculate_monitoring_health
from app.services.incident_service import get_incident_summary
from app.services.problem_service import get_problem_summary
from app.services.change_service import get_change_summary
from app.services.release_service import get_release_summary
from app.services.deployment_service import get_deployment_summary


def _status_rank(status: str) -> int:
    return {
        "Green": 0,
        "Medium": 1,
        "High": 2,
        "Critical": 3,
    }.get(status, 0)


def _merge_status(*statuses: str) -> str:
    return max(statuses, key=_status_rank)


def calculate_operations_control_tower() -> dict:
    monitoring = calculate_monitoring_health()
    incidents = get_incident_summary()
    problems = get_problem_summary()
    changes = get_change_summary()
    releases = get_release_summary()
    deployments = get_deployment_summary()

    overall_status = _merge_status(
        monitoring.get("overall_status", "Green"),
        incidents.get("operational_status", "Green"),
        problems.get("operational_status", "Green"),
        changes.get("operational_status", "Green"),
    )

    affected_components = sorted(
        set(
            monitoring.get("affected_components", [])
        )
    )

    affected_workstreams = sorted(
        set(
            incidents.get("affected_workstreams", [])
            + problems.get("affected_workstreams", [])
            + changes.get("affected_workstreams", [])
        )
    )

    active_alerts = monitoring.get("active_alerts", 0)
    critical_alerts = monitoring.get("critical_alerts", 0)
    high_alerts = monitoring.get("high_alerts", 0)

    open_incidents = incidents.get("open_incidents", 0)
    critical_incidents = incidents.get("critical_incidents", 0)
    high_incidents = incidents.get("high_incidents", 0)

    active_problems = problems.get("active_problems", 0)
    unresolved_root_causes = problems.get(
        "unresolved_root_causes",
        0,
    )

    pending_approval = changes.get("pending_approval", 0)
    active_changes = changes.get("active_changes", 0)

    active_releases = releases.get("active_releases", 0)

    rolled_back_deployments = deployments.get(
        "rolled_back_deployments",
        0,
    )
    failed_validations = deployments.get(
        "failed_validations",
        0,
    )

    executive_actions = []

    if critical_alerts > 0:
        executive_actions.append(
            "Review critical monitoring alerts immediately."
        )

    if critical_incidents > 0:
        executive_actions.append(
            "Prioritize critical incidents and confirm "
            "business impact."
        )

    if unresolved_root_causes > 0:
        executive_actions.append(
            "Continue RCA for problems without an identified "
            "root cause."
        )

    if pending_approval > 0:
        executive_actions.append(
            "Review changes awaiting approval before implementation."
        )

    if rolled_back_deployments > 0:
        executive_actions.append(
            "Review rolled-back deployments and confirm "
            "follow-up corrective actions."
        )

    if failed_validations > 0:
        executive_actions.append(
            "Review failed deployment validation evidence."
        )

    if not executive_actions:
        executive_actions.append(
            "Continue operational monitoring and governance."
        )

    return {
        "overall_status": overall_status,
        "monitoring": {
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
        },
        "incidents": {
            "open_incidents": open_incidents,
            "critical_incidents": critical_incidents,
            "high_incidents": high_incidents,
        },
        "problems": {
            "active_problems": active_problems,
            "unresolved_root_causes": unresolved_root_causes,
        },
        "changes": {
            "active_changes": active_changes,
            "pending_approval": pending_approval,
        },
        "releases": {
            "active_releases": active_releases,
        },
        "deployments": {
            "rolled_back_deployments": rolled_back_deployments,
            "failed_validations": failed_validations,
        },
        "affected_components": affected_components,
        "affected_workstreams": affected_workstreams,
        "executive_actions": executive_actions,
    }
