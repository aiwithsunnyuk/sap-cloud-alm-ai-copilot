from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MonitoringSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class MonitoringStatus(str, Enum):
    OPEN = "Open"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"


class MonitoringEvent(BaseModel):
    event_id: str
    timestamp: datetime
    source: str
    component: str
    event_type: str
    severity: MonitoringSeverity
    status: MonitoringStatus
    message: str
    project_id: str | None = None
    workstream_id: str | None = None


class MonitoringAlert(BaseModel):
    alert_id: str
    event_id: str
    severity: MonitoringSeverity
    status: MonitoringStatus
    detected_at: datetime
    component: str
    message: str
    recommended_action: str
    project_id: str | None = None
    workstream_id: str | None = None
