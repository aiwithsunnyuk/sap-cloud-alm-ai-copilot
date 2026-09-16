from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ProblemStatus(str, Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    ROOT_CAUSE_IDENTIFIED = "Root Cause Identified"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class ProblemPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Problem(BaseModel):
    problem_id: str
    title: str
    description: str
    priority: ProblemPriority
    status: ProblemStatus

    related_incident_ids: list[str]

    affected_component: str
    affected_workstream: str | None = None

    root_cause: str | None = None
    investigation_findings: list[str] = []
    corrective_action: str | None = None
    preventive_action: str | None = None

    opened_at: datetime
    resolved_at: datetime | None = None
