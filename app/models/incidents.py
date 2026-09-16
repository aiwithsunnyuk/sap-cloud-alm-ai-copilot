from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class IncidentSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class IncidentStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class Incident(BaseModel):
    incident_id: str
    alert_id: str
    event_id: str
    title: str
    description: str
    severity: IncidentSeverity
    priority: IncidentPriority
    impact: str
    assigned_team: str
    status: IncidentStatus
    opened_at: datetime
    resolved_at: datetime | None = None
    project_id: str | None = None
    workstream_id: str | None = None
