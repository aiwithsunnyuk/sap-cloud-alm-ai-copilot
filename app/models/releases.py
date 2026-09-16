from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ReleaseType(str, Enum):
    STANDARD = "Standard"
    MAJOR = "Major"
    EMERGENCY = "Emergency"


class ReleaseStatus(str, Enum):
    PLANNED = "Planned"
    READY = "Ready"
    DEPLOYING = "Deploying"
    VALIDATING = "Validating"
    COMPLETED = "Completed"
    FAILED = "Failed"
    ROLLED_BACK = "Rolled Back"


class DeploymentStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"
    ROLLED_BACK = "Rolled Back"


class Release(BaseModel):
    release_id: str
    change_id: str
    title: str
    description: str

    release_type: ReleaseType
    status: ReleaseStatus
    deployment_status: DeploymentStatus

    environment: str
    deployment_package: str

    implementation_steps: list[str] = Field(default_factory=list)
    validation_steps: list[str] = Field(default_factory=list)
    rollback_steps: list[str] = Field(default_factory=list)

    deployment_owner: str
    validation_owner: str

    planned_at: datetime
    deployed_at: datetime | None = None
    completed_at: datetime | None = None

    release_notes: str | None = None
