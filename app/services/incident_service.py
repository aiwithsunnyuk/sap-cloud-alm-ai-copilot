import json
from pathlib import Path

from app.models.incidents import Incident, IncidentStatus


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "incidents.json"
)


def load_incidents() -> list[Incident]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        Incident.model_validate(record)
        for record in records
    ]


def get_incidents() -> list[Incident]:
    return load_incidents()


def get_incident(incident_id: str) -> Incident | None:
    incidents = load_incidents()

    return next(
        (
            incident
            for incident in incidents
            if incident.incident_id == incident_id
        ),
        None,
    )


def get_incident_summary() -> dict:
    incidents = load_incidents()

    open_incidents = [
        incident
        for incident in incidents
        if incident.status != IncidentStatus.CLOSED
        and incident.status != IncidentStatus.RESOLVED
    ]

    critical_count = sum(
        1
        for incident in open_incidents
        if incident.severity.value == "Critical"
    )

    high_count = sum(
        1
        for incident in open_incidents
        if incident.severity.value == "High"
    )

    medium_count = sum(
        1
        for incident in open_incidents
        if incident.severity.value == "Medium"
    )

    if critical_count > 0:
        operational_status = "Critical"
    elif high_count > 0:
        operational_status = "High"
    elif medium_count > 0:
        operational_status = "Medium"
    else:
        operational_status = "Green"

    return {
        "operational_status": operational_status,
        "total_incidents": len(incidents),
        "open_incidents": len(open_incidents),
        "critical_incidents": critical_count,
        "high_incidents": high_count,
        "medium_incidents": medium_count,
        "resolved_incidents": sum(
            1
            for incident in incidents
            if incident.status == IncidentStatus.RESOLVED
        ),
        "affected_workstreams": sorted(
            {
                incident.workstream_id
                for incident in open_incidents
                if incident.workstream_id
            }
        ),
    }
