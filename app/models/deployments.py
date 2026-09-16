from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"
    ROLLED_BACK = "Rolled Back"


class ValidationStatus(str, Enum):
    NOT_STARTED = "Not Started"
    PASSED = "Passed"
    FAILED = "Failed"
    PARTIAL = "Partial"


class RollbackStatus(str, Enum):
    NOT_REQUIRED = "Not Required"
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Deployment(BaseModel):
    deployment_id: str
    release_id: str
    change_id: str

    environment: str
    deployment_package: str

    deployment_status: DeploymentStatus
    validation_status: ValidationStatus
    rollback_status: RollbackStatus

    deployment_owner: str
    validation_owner: str

    validation_checks: list[str] = Field(default_factory=list)
    validation_evidence: list[str] = Field(default_factory=list)

    rollback_required: bool = False

    started_at: datetime
    completed_at: datetime | None = None

    deployment_notes: str | None = None
    validation_notes: str | None = None
    rollback_notes: str | None = None
