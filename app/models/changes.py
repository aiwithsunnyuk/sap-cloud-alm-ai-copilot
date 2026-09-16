from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    STANDARD = "Standard"
    NORMAL = "Normal"
    EMERGENCY = "Emergency"


class ChangePriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class ChangeStatus(str, Enum):
    DRAFT = "Draft"
    ASSESSMENT = "Assessment"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    IMPLEMENTING = "Implementing"
    VALIDATING = "Validating"
    COMPLETED = "Completed"
    REJECTED = "Rejected"


class ChangeRequest(BaseModel):
    change_id: str
    title: str
    description: str

    change_type: ChangeType
    priority: ChangePriority
    status: ChangeStatus

    problem_id: str | None = None
    incident_id: str | None = None
    risk_id: str | None = None

    affected_component: str
    affected_workstream: str | None = None

    business_impact: str
    technical_impact: str
    implementation_plan: list[str] = Field(default_factory=list)
    validation_plan: list[str] = Field(default_factory=list)
    rollback_plan: list[str] = Field(default_factory=list)

    requested_by: str
    assigned_team: str

    approval_required: bool = True
    approved_by: str | None = None

    opened_at: datetime
    planned_implementation_at: datetime | None = None
    completed_at: datetime | None = None
