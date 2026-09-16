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
class MonitoringEventResponse(BaseModel):
    event_id: str
    timestamp: str
    source: str
    component: str
    event_type: str
    severity: str
    status: str
    message: str
    project_id: str | None = None
    workstream_id: str | None = None


class MonitoringAlertResponse(BaseModel):
    alert_id: str
    event_id: str
    severity: str
    status: str
    detected_at: str
    component: str
    message: str
    recommended_action: str
    project_id: str | None = None
    workstream_id: str | None = None


class MonitoringSummaryResponse(BaseModel):
    overall_status: str
    total_events: int
    active_alerts: int
    critical_events: int
    high_events: int
    medium_events: int
    affected_components: list[str]
class MonitoringHealthResponse(BaseModel):
    overall_status: str
    health_score: int
    total_events: int
    active_events: int
    active_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    affected_components: list[str]
    key_drivers: list[str]
    recommended_actions: list[str]
class MonitoringWarningItem(BaseModel):
    warning_type: str
    severity: str
    message: str
    recommended_action: str
    component: str
    event_id: str
    alert_id: str
    project_id: str | None = None
    workstream_id: str | None = None


class CombinedEarlyWarningResponse(BaseModel):
    overall_status: str
    total_warnings: int
    critical_warnings: int
    high_warnings: int
    affected_tasks: list[dict[str, Any]]
    affected_workstreams: list[str]
    executive_action: str
    delivery_warnings: list[dict[str, Any]]
    monitoring_warnings: list[MonitoringWarningItem]
    warnings: list[dict[str, Any]]
class IncidentResponse(BaseModel):
    incident_id: str
    alert_id: str
    event_id: str
    title: str
    description: str
    severity: str
    priority: str
    impact: str
    assigned_team: str
    status: str
    opened_at: str
    resolved_at: str | None = None
    project_id: str | None = None
    workstream_id: str | None = None


class IncidentSummaryResponse(BaseModel):
    operational_status: str
    total_incidents: int
    open_incidents: int
    critical_incidents: int
    high_incidents: int
    medium_incidents: int
    resolved_incidents: int
    affected_workstreams: list[str]
class ProblemResponse(BaseModel):
    problem_id: str
    title: str
    description: str
    priority: str
    status: str
    related_incident_ids: list[str]
    affected_component: str
    affected_workstream: str | None = None
    root_cause: str | None = None
    investigation_findings: list[str]
    corrective_action: str | None = None
    preventive_action: str | None = None
    opened_at: str
    resolved_at: str | None = None


class ProblemSummaryResponse(BaseModel):
    operational_status: str
    total_problems: int
    active_problems: int
    root_cause_identified: int
    unresolved_root_causes: int
    resolved_problems: int
    affected_workstreams: list[str]
