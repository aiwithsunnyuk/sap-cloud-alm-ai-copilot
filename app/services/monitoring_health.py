from app.models.monitoring import MonitoringSeverity, MonitoringStatus
from app.services.monitoring_service import (
    get_active_alerts,
    get_monitoring_events,
)


def calculate_monitoring_health() -> dict:
    events = get_monitoring_events()
    alerts = get_active_alerts()

    critical_alerts = sum(
        1
        for alert in alerts
        if alert.severity == MonitoringSeverity.CRITICAL
    )

    high_alerts = sum(
        1
        for alert in alerts
        if alert.severity == MonitoringSeverity.HIGH
    )

    medium_alerts = sum(
        1
        for alert in alerts
        if alert.severity == MonitoringSeverity.MEDIUM
    )

    low_alerts = sum(
        1
        for alert in alerts
        if alert.severity == MonitoringSeverity.LOW
    )

    active_events = [
        event
        for event in events
        if event.status != MonitoringStatus.RESOLVED
    ]

    affected_components = sorted(
        {
            event.component
            for event in active_events
        }
    )

    repeated_components = []
    component_counts = {}

    for event in active_events:
        component_counts[event.component] = (
            component_counts.get(event.component, 0) + 1
        )

    repeated_components = sorted(
        component
        for component, count in component_counts.items()
        if count > 1
    )

    # Deterministic health score.
    #
    # Critical alert: -30
    # High alert:     -15
    # Medium alert:    -5
    # Low alert:       -1
    #
    # Start from 100 and keep the result within 0-100.

    health_score = (
        100
        - (critical_alerts * 30)
        - (high_alerts * 15)
        - (medium_alerts * 5)
        - (low_alerts * 1)
    )

    health_score = max(0, min(100, health_score))

    if health_score < 40:
        overall_status = "Critical"
    elif health_score < 60:
        overall_status = "High"
    elif health_score < 80:
        overall_status = "Medium"
    else:
        overall_status = "Healthy"

    key_drivers = []

    if critical_alerts > 0:
        key_drivers.append(
            f"{critical_alerts} critical alert(s) require immediate attention."
        )

    if high_alerts > 0:
        key_drivers.append(
            f"{high_alerts} high-severity alert(s) are active."
        )

    if repeated_components:
        key_drivers.append(
            "Repeated operational events detected for: "
            + ", ".join(repeated_components)
            + "."
        )

    if affected_components:
        key_drivers.append(
            f"{len(affected_components)} component(s) are currently affected."
        )

    if not key_drivers:
        key_drivers.append(
            "No significant active operational conditions detected."
        )

    recommended_actions = []

    if critical_alerts > 0:
        recommended_actions.append(
            "Investigate critical alerts and assess business impact."
        )

    if high_alerts > 0:
        recommended_actions.append(
            "Review high-severity alerts with the responsible support team."
        )

    if repeated_components:
        recommended_actions.append(
            "Perform root-cause analysis for repeated component failures."
        )

    if not recommended_actions:
        recommended_actions.append(
            "Continue routine operational monitoring."
        )

    return {
        "overall_status": overall_status,
        "health_score": health_score,
        "total_events": len(events),
        "active_events": len(active_events),
        "active_alerts": len(alerts),
        "critical_alerts": critical_alerts,
        "high_alerts": high_alerts,
        "medium_alerts": medium_alerts,
        "low_alerts": low_alerts,
        "affected_components": affected_components,
        "key_drivers": key_drivers,
        "recommended_actions": recommended_actions,
    }
