import json
from pathlib import Path

from app.models.monitoring import (
    MonitoringAlert,
    MonitoringEvent,
    MonitoringSeverity,
    MonitoringStatus,
)


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "monitoring.json"


def load_monitoring_events() -> list[MonitoringEvent]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [MonitoringEvent.model_validate(record) for record in records]


def get_monitoring_events() -> list[MonitoringEvent]:
    return load_monitoring_events()


def build_alert(event: MonitoringEvent) -> MonitoringAlert | None:
    if event.status == MonitoringStatus.RESOLVED:
        return None

    if event.severity == MonitoringSeverity.CRITICAL:
        action = "Immediate investigation and incident escalation required."

    elif event.severity == MonitoringSeverity.HIGH:
        action = "Investigate the affected component and assess business impact."

    elif event.severity == MonitoringSeverity.MEDIUM:
        action = "Monitor the condition and investigate if the issue persists."

    else:
        action = "Continue monitoring the component."

    return MonitoringAlert(
        alert_id=f"ALT-{event.event_id.replace('EVT-', '')}",
        event_id=event.event_id,
        severity=event.severity,
        status=event.status,
        detected_at=event.timestamp,
        component=event.component,
        message=event.message,
        recommended_action=action,
        project_id=event.project_id,
        workstream_id=event.workstream_id,
    )


def get_active_alerts() -> list[MonitoringAlert]:
    events = load_monitoring_events()

    alerts = []

    for event in events:
        alert = build_alert(event)

        if alert is not None:
            alerts.append(alert)

    return alerts


def get_monitoring_summary() -> dict:
    events = load_monitoring_events()
    alerts = get_active_alerts()

    critical_events = sum(
        1 for event in events
        if event.severity == MonitoringSeverity.CRITICAL
        and event.status != MonitoringStatus.RESOLVED
    )

    high_events = sum(
        1 for event in events
        if event.severity == MonitoringSeverity.HIGH
        and event.status != MonitoringStatus.RESOLVED
    )

    medium_events = sum(
        1 for event in events
        if event.severity == MonitoringSeverity.MEDIUM
        and event.status != MonitoringStatus.RESOLVED
    )

    if critical_events > 0:
        overall_status = "Critical"
    elif high_events > 0:
        overall_status = "High"
    elif medium_events > 0:
        overall_status = "Medium"
    else:
        overall_status = "Green"

    components = sorted(
        {
            event.component
            for event in events
            if event.status != MonitoringStatus.RESOLVED
        }
    )

    return {
        "overall_status": overall_status,
        "total_events": len(events),
        "active_alerts": len(alerts),
        "critical_events": critical_events,
        "high_events": high_events,
        "medium_events": medium_events,
        "affected_components": components,
    }
