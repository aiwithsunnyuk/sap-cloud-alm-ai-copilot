from app.services.early_warning import generate_early_warnings
from app.services.monitoring_service import get_active_alerts


def generate_monitoring_warnings() -> list[dict]:
    """
    Convert active monitoring alerts into early-warning indicators.

    This layer does not modify the existing early-warning engine.
    It adds operational monitoring signals as a separate source.
    """
    alerts = get_active_alerts()

    warnings = []

    for alert in alerts:
        severity = alert.severity.value

        if severity == "Critical":
            warning_type = "Operational Critical Alert"
            message = (
                f"Critical operational condition detected in "
                f"{alert.component}: {alert.message}"
            )
            recommended_action = (
                "Immediately investigate the alert, assess business impact, "
                "and initiate incident escalation."
            )

        elif severity == "High":
            warning_type = "Operational High Alert"
            message = (
                f"High-severity operational condition detected in "
                f"{alert.component}: {alert.message}"
            )
            recommended_action = (
                "Investigate the affected component and assess whether "
                "incident or problem management is required."
            )

        elif severity == "Medium":
            warning_type = "Operational Medium Alert"
            message = (
                f"Medium-severity operational condition detected in "
                f"{alert.component}: {alert.message}"
            )
            recommended_action = (
                "Monitor the condition and investigate if the issue persists."
            )

        else:
            warning_type = "Operational Low Alert"
            message = (
                f"Low-severity operational condition detected in "
                f"{alert.component}: {alert.message}"
            )
            recommended_action = (
                "Continue monitoring the affected component."
            )

        warnings.append(
            {
                "warning_type": warning_type,
                "severity": severity,
                "message": message,
                "recommended_action": recommended_action,
                "component": alert.component,
                "event_id": alert.event_id,
                "alert_id": alert.alert_id,
                "project_id": alert.project_id,
                "workstream_id": alert.workstream_id,
            }
        )

    return warnings


def generate_combined_early_warnings() -> dict:
    """
    Combine delivery early warnings with operational monitoring warnings.

    Existing delivery-warning logic remains unchanged.
    Monitoring warnings are appended as an additional intelligence source.
    """
    delivery_result = generate_early_warnings()
    monitoring_warnings = generate_monitoring_warnings()

    existing_warnings = delivery_result.get("warnings", [])

    combined_warnings = existing_warnings + monitoring_warnings

    critical_count = sum(
        1
        for warning in combined_warnings
        if warning.get("severity") == "Critical"
    )

    high_count = sum(
        1
        for warning in combined_warnings
        if warning.get("severity") == "High"
    )

    if critical_count > 0:
        overall_status = "Critical"
        executive_action = (
            "Immediate attention required. Review critical delivery "
            "and operational warnings and initiate appropriate escalation."
        )

    elif high_count > 0:
        overall_status = "High"
        executive_action = (
            "Elevated delivery or operational risk detected. "
            "Review high-severity warnings and affected components."
        )

    elif combined_warnings:
        overall_status = "Medium"
        executive_action = (
            "Monitor emerging delivery and operational conditions "
            "and confirm mitigation actions."
        )

    else:
        overall_status = "Green"
        executive_action = (
            "No significant delivery or operational early-warning "
            "conditions detected."
        )

    affected_tasks = delivery_result.get("affected_tasks", [])

    affected_workstreams = sorted(
        {
            warning.get("workstream_id")
            for warning in monitoring_warnings
            if warning.get("workstream_id")
        }
    )

    return {
        "overall_status": overall_status,
        "total_warnings": len(combined_warnings),
        "critical_warnings": critical_count,
        "high_warnings": high_count,
        "affected_tasks": affected_tasks,
        "affected_workstreams": affected_workstreams,
        "executive_action": executive_action,
        "delivery_warnings": existing_warnings,
        "monitoring_warnings": monitoring_warnings,
        "warnings": combined_warnings,
    }
