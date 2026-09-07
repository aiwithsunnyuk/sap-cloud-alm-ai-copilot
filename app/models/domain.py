from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TaskStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DependencyType(str, Enum):
    BLOCKS = "Blocks"
    DEPENDS_ON = "Depends On"
    RELATED = "Related"


class Project(BaseModel):
    project_id: str
    name: str
    description: str | None = None
    status: str = "Active"


class Workstream(BaseModel):
    workstream_id: str
    project_id: str
    name: str
    owner: str


class Task(BaseModel):
    task_id: str
    project_id: str
    workstream_id: str
    name: str
    owner: str
    priority: Priority
    status: TaskStatus
    planned_end: date
    percent_complete: int = Field(ge=0, le=100)


class Dependency(BaseModel):
    dependency_id: str
    from_task: str
    to_task: str
    type: DependencyType
    status: str = "Open"


class Risk(BaseModel):
    risk_id: str
    project_id: str
    workstream_id: str
    title: str
    description: str
    severity: RiskLevel
    probability: RiskLevel
    status: str = "Open"
    mitigation: str


class RiskAssessment(BaseModel):
    task_id: str
    risk_score: int
    risk_level: RiskLevel
    reasons: list[str]
    recommendations: list[str]
