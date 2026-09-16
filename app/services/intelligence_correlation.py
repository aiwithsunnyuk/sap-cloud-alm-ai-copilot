from app.models.intelligence_correlation import (
    CorrelatedObject,
    OperationalCorrelation,
    CorrelationResponse,
)
from app.services.monitoring_service import (
    get_active_alerts,
    get_monitoring_events,
)
from app.services.incident_service import get_incidents
from app.services.problem_service import get_problems
from app.services.change_service import get_changes
from app.services.release_service import get_releases
from app.services.deployment_service import get_deployments


def _value(value) -> str:
    return getattr(value, "value", value)


def generate_operational_correlations() -> CorrelationResponse:
    alerts = get_active_alerts()
    events = get_monitoring_events()
    incidents = get_incidents()
    problems = get_problems()
    changes = get_changes()
    releases = get_releases()
    deployments = get_deployments()

    event_by_id = {event.event_id: event for event in events}
    problem_by_id = {problem.problem_id: problem for problem in problems}
    change_by_id = {change.change_id: change for change in changes}
    release_by_id = {release.release_id: release for release in releases}
    deployment_by_release = {
        deployment.release_id: deployment for deployment in deployments
    }

    correlations: list[OperationalCorrelation] = []

    for incident in incidents:
        chain: list[str] = []

        event_id = getattr(incident, "event_id", None)
        alert_id = getattr(incident, "alert_id", None)

        if event_id:
            chain.append(event_id)

        if alert_id:
            chain.append(alert_id)

        chain.append(incident.incident_id)

        related_objects = [
            CorrelatedObject(
                object_type="Incident",
                object_id=incident.incident_id,
            )
        ]

        severity = _value(getattr(incident, "severity", "Medium"))

        related_problem = None
        for problem in problems:
            related_incident_ids = getattr(problem, "related_incident_ids", [])
            if incident.incident_id in related_incident_ids:
                related_problem = problem
                break

        if related_problem:
            chain.append(related_problem.problem_id)
            related_objects.append(
                CorrelatedObject(
                    object_type="Problem",
                    object_id=related_problem.problem_id,
                )
            )

            change = next(
                (
                    item
                    for item in changes
                    if getattr(item, "problem_id", None)
                    == related_problem.problem_id
                    or getattr(item, "incident_id", None)
                    == incident.incident_id
                ),
                None,
            )

            if change:
                chain.append(change.change_id)
                related_objects.append(
                    CorrelatedObject(
                        object_type="Change",
                        object_id=change.change_id,
                    )
                )

                release = next(
                    (
                        item
                        for item in releases
                        if getattr(item, "change_id", None) == change.change_id
                    ),
                    None,
                )

                if release:
                    chain.append(release.release_id)
                    related_objects.append(
                        CorrelatedObject(
                            object_type="Release",
                            object_id=release.release_id,
                        )
                    )

                    deployment = deployment_by_release.get(release.release_id)

                    if deployment:
                        chain.append(deployment.deployment_id)
                        related_objects.append(
                            CorrelatedObject(
                                object_type="Deployment",
                                object_id=deployment.deployment_id,
                            )
                        )

                        deployment_status = _value(
                            getattr(
                                deployment,
                                "deployment_status",
                                "Unknown",
                            )
                        )
                        validation_status = _value(
                            getattr(
                                deployment,
                                "validation_status",
                                "Unknown",
                            )
                        )
                        rollback_status = _value(
                            getattr(
                                deployment,
                                "rollback_status",
                                "Unknown",
                            )
                        )

                        if deployment_status == "Rolled Back":
                            severity = "Critical"

                        evidence = [
                            f"Incident: {incident.incident_id}",
                            f"Problem: {related_problem.problem_id}",
                            f"Change: {change.change_id}",
                            f"Release: {release.release_id}",
                            f"Deployment: {deployment.deployment_id}",
                            f"Deployment status: {deployment_status}",
                            f"Validation status: {validation_status}",
                            f"Rollback status: {rollback_status}",
                        ]
                    else:
                        evidence = [
                            f"Incident: {incident.incident_id}",
                            f"Problem: {related_problem.problem_id}",
                            f"Change: {change.change_id}",
                            f"Release: {release.release_id}",
                        ]
                else:
                    evidence = [
                        f"Incident: {incident.incident_id}",
                        f"Problem: {related_problem.problem_id}",
                        f"Change: {change.change_id}",
                    ]
            else:
                evidence = [
                    f"Incident: {incident.incident_id}",
                    f"Problem: {related_problem.problem_id}",
                ]
        else:
            evidence = [
                f"Incident: {incident.incident_id}",
                "No linked problem was identified in the current dataset.",
            ]

        event = event_by_id.get(event_id)
        if event:
            evidence.append(
                f"Monitoring event: {event.event_id}"
            )

        alert = next(
            (
                item
                for item in alerts
                if getattr(item, "alert_id", None) == alert_id
            ),
            None,
        )

        if alert:
            evidence.append(
                f"Active alert: {alert.alert_id}"
            )

        correlations.append(
            OperationalCorrelation(
                correlation_id=f"COR-{incident.incident_id}",
                severity=severity,
                title=(
                    f"Operational chain detected for "
                    f"{incident.incident_id}"
                ),
                summary=(
                    "Cross-domain operational objects were correlated "
                    "from monitoring through incident and downstream "
                    "delivery or deployment records."
                ),
                related_objects=related_objects,
                causal_chain=chain,
                evidence=evidence,
                recommended_action=(
                    "Review the correlated chain from incident through "
                    "change, release, and deployment before taking "
                    "further operational action."
                ),
            )
        )

    critical_count = sum(
        1 for item in correlations if item.severity == "Critical"
    )
    high_count = sum(
        1 for item in correlations if item.severity == "High"
    )

    overall_status = "Green"

    if critical_count > 0:
        overall_status = "Critical"
    elif high_count > 0:
        overall_status = "High"
    elif correlations:
        overall_status = "Medium"

    return CorrelationResponse(
        overall_status=overall_status,
        total_correlations=len(correlations),
        critical_correlations=critical_count,
        high_correlations=high_count,
        correlations=correlations,
    )
