from typing import Any

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    service: str


class RiskSummaryResponse(BaseModel):
    total_tasks: int
    critical: int
    high: int
    medium: int
    low: int
    assessments: list[dict[str, Any]]


class HighestRiskTaskResponse(BaseModel):
    task_id: str
    task_name: str
    risk_score: int
    risk_level: str


class WorkstreamSummaryItem(BaseModel):
    workstream_id: str
    total_tasks: int
    critical: int
    high: int
    medium: int
    low: int
    average_risk_score: float
    blocked_tasks: int
    highest_risk_task: HighestRiskTaskResponse
    overall_health: str


class WorkstreamSummaryResponse(BaseModel):
    total_workstreams: int
    workstreams: list[WorkstreamSummaryItem]


class ProjectSummaryResponse(BaseModel):
    project_id: str
    project_name: str
    customer: str | None = None
    status: str | None = None
    start_date: str | None = None
    target_date: str | None = None
    overall_health: str
    total_tasks: int
    critical: int
    high: int
    medium: int
    low: int
    average_risk_score: float
    blocked_tasks: int
    highest_risk_task: dict[str, Any] | None = None


class HealthExplanationResponse(BaseModel):
    health_explanation: str
    key_drivers: list[str]
    recommended_actions: list[str]


class EarlyWarningItem(BaseModel):
    """
    API representation of an early-warning indicator.

    Different warning types can contain different fields, so additional
    fields are deliberately preserved rather than discarded.
    """

    model_config = ConfigDict(extra="allow")

    warning_type: str
    severity: str
    task_id: str | None = None
    task_name: str | None = None
    risk_score: float | None = None
    risk_id: str | None = None
    workstream_id: str | None = None
    title: str | None = None
    message: str
    recommended_action: str | None = None


class EarlyWarningResponse(BaseModel):
    overall_status: str
    total_warnings: int
    critical_warnings: int
    high_warnings: int
    affected_tasks: list[dict[str, Any]]
    executive_action: str
    warnings: list[EarlyWarningItem]


class RiskHistoryItem(BaseModel):
    snapshot_date: str
    task_id: str
    risk_score: int
    risk_level: str


class RiskHistoryResponse(BaseModel):
    task_id: str
    snapshots: list[RiskHistoryItem]


class RiskTrendResponse(BaseModel):
    task_id: str
    snapshot_count: int
    starting_risk_score: int | None
    current_risk_score: int | None
    risk_change: int | None
    risk_velocity: float | None
    trend: str
    severity_transition: str | None
