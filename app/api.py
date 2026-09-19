from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from app.models.intelligence_decision_brief import DecisionBriefResponse
from app.models.intelligence_recommendation import RecommendationResponse
from app.models.intelligence_explanation import ExplanationResponse
from app.models.intelligence_correlation import CorrelationResponse
from app.models.intelligence import IntelligenceResponse
from app.models.responses import (
    HealthResponse,
    RiskSummaryResponse,
    WorkstreamSummaryResponse,
    ProjectSummaryResponse,
    HealthExplanationResponse,
    EarlyWarningResponse,
    RiskHistoryResponse,
    RiskTrendResponse,
    MonitoringEventResponse,
    MonitoringAlertResponse,
    MonitoringSummaryResponse,
    MonitoringHealthResponse,
    MonitoringWarningItem,
    CombinedEarlyWarningResponse,
    IncidentResponse,
    IncidentSummaryResponse,
    ProblemResponse,
    ProblemSummaryResponse,
    ChangeResponse,
    ChangeSummaryResponse,
    ReleaseResponse,
    ReleaseSummaryResponse,
    ReleaseGovernanceResponse,
    DeploymentResponse,
    DeploymentSummaryResponse,
    OperationsControlTowerResponse,
)
from app.services.release_service import (
    get_releases,
    get_release,
    get_release_summary,
)
from app.services.release_governance import validate_release_governance

from app.services.change_service import (
    get_changes,
    get_change,
    get_change_summary,
)

from app.services.problem_service import (
    get_problems,
    get_problem,
    get_problem_summary,
)
from app.services.incident_service import (
    get_incidents,
    get_incident,
    get_incident_summary,
)
from app.services.monitoring_health import calculate_monitoring_health
from app.services.risk_engine import calculate_risk_score
from app.services.historical_risk import get_task_history
from app.services.risk_trend import calculate_risk_trend
from app.services.monitoring_service import (
    get_monitoring_events,
    get_active_alerts,
    get_monitoring_summary,
)

from app.services.historical_risk import get_task_history
from app.services.risk_trend import calculate_risk_trend

app = FastAPI(
    title="SAP Cloud ALM AI Copilot",
    version="0.1.0",
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str):
    path = DATA_DIR / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {filename}",
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "healthy",
        "service": "sap-cloud-alm-ai-copilot",
    }


@app.get("/projects")
def get_projects():
    return load_json("projects.json")


from app.services.task_service import get_application_tasks

from app.models.calm_source_status import CalmSourceStatus
from app.services.calm_source_status import get_calm_source_status

@app.get(
    "/integration/calm/status",
    response_model=CalmSourceStatus,
)
def get_calm_integration_status() -> CalmSourceStatus:
    """Return safe SAP Cloud ALM data-source health information."""
    return get_calm_source_status()


@app.get("/tasks")
def get_tasks(
    project_id: str | None = None,
    limit: int | None = None,
):
    return get_application_tasks(
        project_id=project_id,
        limit=limit,
    )

@app.get("/risks")
def get_risks():
    return load_json("risks.json")


@app.get("/dependencies")
def get_dependencies():
    return load_json("dependencies.json")


@app.get("/tasks/{task_id}/risk")
def get_task_risk(task_id: str):
    tasks = load_json("tasks.json")
    dependencies = load_json("dependencies.json")
    risks = load_json("risks.json")

    task = next(
        (item for item in tasks if item.get("task_id") == task_id),
        None,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task not found: {task_id}",
        )

    return calculate_risk_score(
        task=task,
        dependencies=dependencies,
        risks=risks,
    )


@app.get("/risks/summary", response_model=RiskSummaryResponse)
def risk_summary():
    tasks = load_json("tasks.json")
    dependencies = load_json("dependencies.json")
    risks = load_json("risks.json")

    assessments = []

    for task in tasks:
        assessment = calculate_risk_score(
            task=task,
            dependencies=dependencies,
            risks=risks,
        )
        assessments.append(assessment)

    summary = {
        "total_tasks": len(assessments),
        "critical": sum(
            1 for item in assessments
            if item["risk_level"] == "Critical"
        ),
        "high": sum(
            1 for item in assessments
            if item["risk_level"] == "High"
        ),
        "medium": sum(
            1 for item in assessments
            if item["risk_level"] == "Medium"
        ),
        "low": sum(
            1 for item in assessments
            if item["risk_level"] == "Low"
        ),
        "assessments": assessments,
    }

    return summary

@app.get("/workstreams/summary", response_model=WorkstreamSummaryResponse)
def workstreams_summary():
    tasks = load_json("tasks.json")
    dependencies = load_json("dependencies.json")
    risks = load_json("risks.json")

    assessments = []

    for task in tasks:
        assessments.append(
            calculate_risk_score(
                task=task,
                dependencies=dependencies,
                risks=risks,
            )
        )

    workstreams = {}

    for assessment in assessments:
        workstream_id = assessment.get("workstream_id", "UNKNOWN")

        if workstream_id not in workstreams:
            workstreams[workstream_id] = []

        workstreams[workstream_id].append(assessment)

    summaries = []

    for workstream_id, items in workstreams.items():
        risk_scores = [item.get("risk_score", 0) for item in items]

        highest_risk_task = max(
            items,
            key=lambda item: item.get("risk_score", 0),
        )

        blocked_tasks = [
            item for item in items
            if item.get("status") == "Blocked"
        ]

        critical = sum(
            1 for item in items
            if item.get("risk_level") == "Critical"
        )

        high = sum(
            1 for item in items
            if item.get("risk_level") == "High"
        )

        medium = sum(
            1 for item in items
            if item.get("risk_level") == "Medium"
        )

        low = sum(
            1 for item in items
            if item.get("risk_level") == "Low"
        )

        average_risk_score = round(
            sum(risk_scores) / len(risk_scores),
            2,
        ) if risk_scores else 0

        if critical > 0:
            overall_health = "Red"
        elif high > 0:
            overall_health = "Amber"
        else:
            overall_health = "Green"

        summaries.append(
            {
                "workstream_id": workstream_id,
                "total_tasks": len(items),
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "average_risk_score": average_risk_score,
                "blocked_tasks": len(blocked_tasks),
                "highest_risk_task": {
                    "task_id": highest_risk_task.get("task_id"),
                    "task_name": highest_risk_task.get("task_name"),
                    "risk_score": highest_risk_task.get("risk_score"),
                    "risk_level": highest_risk_task.get("risk_level"),
                },
                "overall_health": overall_health,
            }
        )

    return {
        "total_workstreams": len(summaries),
        "workstreams": summaries,
    }
@app.get("/projects/{project_id}/summary", response_model=ProjectSummaryResponse)
def project_summary(project_id: str):
    projects = load_json("projects.json")
    tasks = load_json("tasks.json")
    dependencies = load_json("dependencies.json")
    risks = load_json("risks.json")

    project = next(
        (item for item in projects if item.get("project_id") == project_id),
        None,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail=f"Project not found: {project_id}",
        )

    project_tasks = [
        task for task in tasks
        if task.get("project_id") == project_id
    ]

    assessments = []

    for task in project_tasks:
        assessment = calculate_risk_score(
            task=task,
            dependencies=dependencies,
            risks=risks,
        )
        assessments.append(assessment)

    risk_scores = [
        item.get("risk_score", 0)
        for item in assessments
    ]

    critical = sum(
        1
        for item in assessments
        if item.get("risk_level") == "Critical"
    )

    high = sum(
        1
        for item in assessments
        if item.get("risk_level") == "High"
    )

    medium = sum(
        1
        for item in assessments
        if item.get("risk_level") == "Medium"
    )

    low = sum(
        1
        for item in assessments
        if item.get("risk_level") == "Low"
    )

    blocked_tasks = [
        task for task in project_tasks
        if task.get("status") == "Blocked"
    ]

    average_risk_score = round(
        sum(risk_scores) / len(risk_scores),
        2,
    ) if risk_scores else 0

    if critical > 0:
        overall_health = "Red"
    elif high > 0:
        overall_health = "Amber"
    else:
        overall_health = "Green"

    highest_risk_task = (
        max(
            assessments,
            key=lambda item: item.get("risk_score", 0),
        )
        if assessments
        else None
    )

    return {
        "project_id": project_id,
        "project_name": project.get("name"),
        "customer": project.get("customer"),
        "status": project.get("status"),
        "start_date": project.get("start_date"),
        "target_date": project.get("target_date"),
        "overall_health": overall_health,
        "total_tasks": len(project_tasks),
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "average_risk_score": average_risk_score,
        "blocked_tasks": len(blocked_tasks),
        "highest_risk_task": highest_risk_task,
    }
@app.get("/workstreams/summary")
def get_workstream_summary():
    tasks = load_json("tasks.json")
    dependencies = load_json("dependencies.json")
    risks = load_json("risks.json")

    workstreams = {}

    for task in tasks:
        workstream_id = task.get("workstream_id", "UNKNOWN")

        assessment = calculate_risk_score(
            task=task,
            dependencies=dependencies,
            risks=risks,
        )

        workstreams.setdefault(workstream_id, []).append(assessment)

    summaries = []

    for workstream_id, items in workstreams.items():
        critical = sum(
            1 for item in items
            if item.get("risk_level") == "Critical"
        )

        high = sum(
            1 for item in items
            if item.get("risk_level") == "High"
        )

        medium = sum(
            1 for item in items
            if item.get("risk_level") == "Medium"
        )

        low = sum(
            1 for item in items
            if item.get("risk_level") == "Low"
        )

        risk_scores = [
            item.get("risk_score", 0)
            for item in items
        ]

        average_risk_score = round(
            sum(risk_scores) / len(risk_scores),
            2
        ) if risk_scores else 0

        blocked_tasks = [
            item for item in items
            if item.get("status") == "Blocked"
        ]

        highest_risk_task = max(
            items,
            key=lambda item: item.get("risk_score", 0)
        )

        if critical > 0:
            overall_health = "Red"
        elif high > 0:
            overall_health = "Amber"
        else:
            overall_health = "Green"

        summaries.append({
            "workstream_id": workstream_id,
            "total_tasks": len(items),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "average_risk_score": average_risk_score,
            "blocked_tasks": len(blocked_tasks),
            "highest_risk_task": {
                "task_id": highest_risk_task.get("task_id"),
                "task_name": highest_risk_task.get("task_name"),
                "risk_score": highest_risk_task.get("risk_score"),
                "risk_level": highest_risk_task.get("risk_level"),
            },
            "overall_health": overall_health,
        })

    return {
        "total_workstreams": len(summaries),
        "workstreams": summaries,
    }

from app.services.health_explainer import explain_project_health

@app.get("/workstreams/{workstream_id}/health", response_model=HealthExplanationResponse)
def get_workstream_health(workstream_id: str):
    summary = get_workstream_summary()

    for workstream in summary.get("workstreams", []):
        if workstream.get("workstream_id") == workstream_id:
            return explain_project_health(workstream)

    return {"detail": "Not Found"}

from app.services.early_warning import generate_early_warnings


@app.get("/api/v1/early-warnings", response_model=EarlyWarningResponse)
def early_warnings():
    """Return project early-warning indicators."""
    return generate_early_warnings()


@app.get(
    "/api/v1/tasks/{task_id}/risk-history",
    response_model=RiskHistoryResponse,
)
def get_risk_history(task_id: str):
    history = get_task_history(task_id)

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No risk history found for task {task_id}",
        )

    return {
        "task_id": task_id,
        "snapshots": history,
    }


@app.get(
    "/api/v1/tasks/{task_id}/risk-trend",
    response_model=RiskTrendResponse,
)
def get_risk_trend(task_id: str):
    trend = calculate_risk_trend(task_id)

    if trend["snapshot_count"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No risk history found for task {task_id}",
        )

    return trend
@app.get(
    "/monitoring/events",
    response_model=list[MonitoringEventResponse],
)
def get_monitoring_events_api():
    return [
        event.model_dump(mode="json")
        for event in get_monitoring_events()
    ]


@app.get(
    "/monitoring/alerts",
    response_model=list[MonitoringAlertResponse],
)
def get_monitoring_alerts_api():
    return [
        alert.model_dump(mode="json")
        for alert in get_active_alerts()
    ]


@app.get(
    "/monitoring/summary",
    response_model=MonitoringSummaryResponse,
)
def get_monitoring_summary_api():
    return get_monitoring_summary()
@app.get(
    "/monitoring/health",
    response_model=MonitoringHealthResponse,
)
def get_monitoring_health_api():
    return calculate_monitoring_health()
@app.get(
    "/api/v1/monitoring-early-warnings",
    response_model=CombinedEarlyWarningResponse,
)
def get_monitoring_early_warnings_api():
    return generate_combined_early_warnings()
@app.get(
    "/incidents",
    response_model=list[IncidentResponse],
)
def get_incidents_api():
    return [
        incident.model_dump(mode="json")
        for incident in get_incidents()
    ]


@app.get(
    "/incidents",
    response_model=list[IncidentResponse],
)
def get_incidents_api():
    return [
        incident.model_dump(mode="json")
        for incident in get_incidents()
    ]


@app.get(
    "/incidents/summary",
    response_model=IncidentSummaryResponse,
)
def get_incident_summary_api():
    return get_incident_summary()


@app.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident_api(incident_id: str):
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=f"Incident not found: {incident_id}",
        )

    return incident.model_dump(mode="json")
@app.get(
    "/problems",
    response_model=list[ProblemResponse],
)
def get_problems_api():
    return [
        problem.model_dump(mode="json")
        for problem in get_problems()
    ]


@app.get(
    "/problems/summary",
    response_model=ProblemSummaryResponse,
)
def get_problem_summary_api():
    return get_problem_summary()


@app.get(
    "/problems/{problem_id}",
    response_model=ProblemResponse,
)
def get_problem_api(problem_id: str):
    problem = get_problem(problem_id)

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail=f"Problem not found: {problem_id}",
        )

    return problem.model_dump(mode="json")
@app.get(
    "/changes",
    response_model=list[ChangeResponse],
)
def get_changes_api():
    return [
        change.model_dump(mode="json")
        for change in get_changes()
    ]


@app.get(
    "/changes/summary",
    response_model=ChangeSummaryResponse,
)
def get_change_summary_api():
    return get_change_summary()


@app.get(
    "/changes/{change_id}",
    response_model=ChangeResponse,
)
def get_change_api(change_id: str):
    change = get_change(change_id)

    if change is None:
        raise HTTPException(
            status_code=404,
            detail=f"Change not found: {change_id}",
        )

    return change.model_dump(mode="json")
@app.get(
    "/releases",
    response_model=list[ReleaseResponse],
)
def get_releases_api():
    return [
        release.model_dump(mode="json")
        for release in get_releases()
    ]


@app.get(
    "/releases/summary",
    response_model=ReleaseSummaryResponse,
)
def get_release_summary_api():
    return get_release_summary()


@app.get(
    "/releases/{release_id}",
    response_model=ReleaseResponse,
)
def get_release_api(release_id: str):
    release = get_release(release_id)

    if release is None:
        raise HTTPException(
            status_code=404,
            detail=f"Release not found: {release_id}",
        )

    return release.model_dump(mode="json")



@app.get(
    "/releases/{release_id}/governance",
    response_model=ReleaseGovernanceResponse,
)
def get_release_governance_api(release_id: str):
    return validate_release_governance(release_id)

from app.services.deployment_service import (
    get_deployments,
    get_deployment,
    get_deployment_summary,
)


@app.get(
    "/deployments",
    response_model=list[DeploymentResponse],
)
def get_deployments_api():
    return [
        deployment.model_dump(mode="json")
        for deployment in get_deployments()
    ]


@app.get(
    "/deployments/summary",
    response_model=DeploymentSummaryResponse,
)
def get_deployment_summary_api():
    return get_deployment_summary()


@app.get(
    "/deployments/{deployment_id}",
    response_model=DeploymentResponse,
)
def get_deployment_api(deployment_id: str):
    deployment = get_deployment(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail=f"Deployment not found: {deployment_id}",
        )

    return deployment.model_dump(mode="json")

from app.services.operations_control_tower import calculate_operations_control_tower
from app.services.intelligence_service import generate_operational_intelligence
from app.services.intelligence_correlation import generate_operational_correlations
from app.services.intelligence_explanation import generate_operational_explanations
from app.services.intelligence_recommendation import generate_operational_recommendations
from app.services.intelligence_decision_brief import generate_operational_decision_brief
from app.models.copilot import CopilotQueryRequest
from app.models.copilot import CopilotIntent
from app.models.copilot_response import CopilotResponse
from app.models.copilot_session import CopilotSessionSummary
from app.models.copilot_context import CopilotContextTurn
from app.services.copilot_context_service import (
    add_turn,
    contextualize_question,
)
from app.services.copilot_context_service import (
    get_latest_entity_context,
    get_conversation_evidence,
)
from app.services.copilot_entity_capture import capture_entity_context
from app.services.copilot_followup_resolver import resolve_follow_up_entity
from app.services.copilot_entity_resolver import resolve_entity
from app.services.incident_service import get_incident
from app.services.deployment_service import get_deployment
from app.services.copilot_response_service import generate_copilot_response
from app.services.copilot_session_service import get_session_summary


@app.get(
    "/operations/control-tower",
    response_model=OperationsControlTowerResponse,
)
def get_operations_control_tower_api():
    return calculate_operations_control_tower()

@app.get("/intelligence/operational", response_model=IntelligenceResponse)
def get_operational_intelligence_api():
    """Get deterministic operational intelligence insights."""
    return generate_operational_intelligence()

@app.get("/intelligence/correlations", response_model=CorrelationResponse)
def get_operational_correlations_api():
    """Get cross-domain operational correlations."""
    return generate_operational_correlations()

@app.get("/intelligence/explanations", response_model=ExplanationResponse)
def get_operational_explanations_api():
    """Get deterministic explanations for operational correlations."""
    return generate_operational_explanations()

@app.get(
    "/intelligence/recommendations",
    response_model=RecommendationResponse,
)
def get_operational_recommendations_api():
    """Get prioritized operational recommendations."""
    return generate_operational_recommendations()

@app.get(
    "/intelligence/decision-brief",
    response_model=DecisionBriefResponse,
)
def get_operational_decision_brief_api():
    """Get the consolidated operational decision brief."""
    return generate_operational_decision_brief()

from app.models.copilot_agent_evaluation import (
    CopilotAgentEvaluation,
    CopilotAgentEvaluationRequest,
)
from app.services.copilot_agent_evaluation import evaluate_agent_execution

from app.models.copilot_decision_response import (
    CopilotDecisionOrchestrationResponse,
)
from app.models.copilot_multi_agent import CopilotMultiAgentDecisionRequest
from app.services.copilot_decision_orchestration import (
    orchestrate_decision_with_confidence,
)

from app.models.copilot_decision_assessment import CopilotDecisionAssessment
from app.models.copilot_decision_approval_request import CopilotDecisionApprovalRequest
from app.models.copilot_multi_agent import CopilotMultiAgentDecisionRequest
from app.services.copilot_decision_assessment import assess_multi_agent_decision

from app.models.copilot_approval import (
    CopilotApprovalRequest,
    CopilotApprovalResult,
)
from app.services.copilot_approval_service import evaluate_approval

from app.models.copilot_approval_audit import (
    CopilotApprovalAuditRecord,
    CopilotApprovalAuditSummary,
)
from app.services.copilot_approval_audit import (
    get_approval_audit_record,
    get_approval_audit_records,
    get_approval_audit_summary,
)

from app.models.copilot_decision_approval import CopilotDecisionApprovalResult
from app.models.copilot_decision_assessment import CopilotDecisionAssessment
from app.services.copilot_decision_approval import evaluate_decision_approval

@app.post("/copilot/query", response_model=CopilotResponse)
def copilot_query(request: CopilotQueryRequest) -> CopilotResponse:
    """Answer a natural-language Copilot question using grounded project intelligence."""

    previous_entity_context = None
    latest_context = contextualize_question(
        request.question,
        request.conversation_id,
    )

    contextual_request = CopilotQueryRequest(
        question=latest_context,
        conversation_id=request.conversation_id,
    )

    # Resolve explicit follow-up references against the previous entity.
    previous_entity_context = get_latest_entity_context(
        request.conversation_id,
    )

    follow_up_entity = resolve_follow_up_entity(
        request.question,
        previous_entity_context,
    )

    if follow_up_entity is not None:
        if follow_up_entity.entity_type == "incident":
            incident = get_incident(follow_up_entity.entity_id)

            if incident is not None:
                response = CopilotResponse(
                    question=request.question,
                    intent=CopilotIntent.INCIDENT,
                    confidence=1.0,
                    answer=(
                        f"{incident.incident_id}: "
                        f"{incident.title}. "
                        f"{incident.description}"
                    ),
                    evidence=[
                        f"Incident: {incident.incident_id}",
                        f"Severity: {incident.severity.value}",
                        f"Priority: {incident.priority.value}",
                        f"Status: {incident.status.value}",
                    ],
                    source_capability="Incident Intelligence",
                    source_endpoint="/incidents/{incident_id}",
                    trace=[
                        "Conversation Context",
                        "Follow-up Entity Resolver",
                        "Incident Service",
                    ],
                    grounded=True,
                    action_required=(
                        incident.status.value != "Resolved"
                    ),
                    approval_required=False,
                )
            else:
                response = generate_copilot_response(
                    contextual_request
                )
        else:
            response = generate_copilot_response(
                contextual_request
            )
    else:
        response = generate_copilot_response(
            contextual_request
        )

    # Keep the public response anchored to the user's original question.
    response.question = request.question

    # Add an auditable metadata trail for conversational execution.
    trace = list(response.trace)

    if "Conversation Context" not in trace:
        trace.append("Conversation Context")

    if previous_entity_context is not None:
        previous_primary = previous_entity_context.primary

        if previous_primary is not None:
            previous_entry = (
                f"Previous Entity: "
                f"{previous_primary.entity_type}:"
                f"{previous_primary.entity_id}"
            )

            if previous_entry not in trace:
                trace.append(previous_entry)

    if follow_up_entity is not None:
        resolved_entry = (
            f"Resolved Entity: "
            f"{follow_up_entity.entity_type}:"
            f"{follow_up_entity.entity_id}"
        )

        if resolved_entry not in trace:
            trace.append(resolved_entry)

    if "Evidence Continuity" not in trace:
        trace.append("Evidence Continuity")

    response.trace = trace

    # Preserve the established evidence trail across conversation turns.
    prior_evidence = get_conversation_evidence(
        request.conversation_id,
    )

    cumulative_evidence = list(prior_evidence)

    for item in response.evidence:
        if item not in cumulative_evidence:
            cumulative_evidence.append(item)

    response.evidence = cumulative_evidence

    entity_context = capture_entity_context(
        question=request.question,
        answer=response.answer,
        evidence=response.evidence,
    )

    add_turn(
        request.conversation_id,
        CopilotContextTurn(
            question=request.question,
            intent=response.intent.value,
            answer=response.answer,
            source_capability=response.source_capability,
            grounded=response.grounded,
            evidence=response.evidence,
            entity_context=entity_context,
        ),
    )

    return response

@app.post(
    "/copilot/decisions",
    response_model=CopilotDecisionOrchestrationResponse,
)
def copilot_decision(
    request: CopilotMultiAgentDecisionRequest,
) -> CopilotDecisionOrchestrationResponse:
    """Build a read-only multi-agent decision candidate with support confidence."""
    return orchestrate_decision_with_confidence(request)


@app.post(
    "/copilot/agents/evaluate",
    response_model=CopilotAgentEvaluation,
)
def evaluate_copilot_agent(
    request: CopilotAgentEvaluationRequest,
) -> CopilotAgentEvaluation:
    """Evaluate an agent execution for governance, grounding, execution and trace quality."""
    return evaluate_agent_execution(request)


@app.post(
    "/copilot/decisions/orchestrate",
    response_model=CopilotDecisionAssessment,
)
def orchestrate_copilot_decision(
    request: CopilotMultiAgentDecisionRequest,
) -> CopilotDecisionAssessment:
    """Build a deterministic multi-agent decision assessment."""
    return assess_multi_agent_decision(request)


@app.post(
    "/copilot/approvals/evaluate",
    response_model=CopilotApprovalResult,
)
def evaluate_copilot_approval(
    request: CopilotApprovalRequest,
) -> CopilotApprovalResult:
    """Evaluate whether a decision may proceed through human governance."""
    return evaluate_approval(request)


@app.get(
    "/copilot/approvals/audit",
    response_model=list[CopilotApprovalAuditRecord],
)
def get_copilot_approval_audit() -> list[CopilotApprovalAuditRecord]:
    """Return recorded human-approval audit records."""
    return get_approval_audit_records()


@app.get(
    "/copilot/approvals/audit/summary",
    response_model=CopilotApprovalAuditSummary,
)
def get_copilot_approval_audit_summary() -> CopilotApprovalAuditSummary:
    """Return an approval-audit status summary."""
    return get_approval_audit_summary()


@app.get(
    "/copilot/approvals/audit/{audit_id}",
    response_model=CopilotApprovalAuditRecord,
)
def get_copilot_approval_audit_record(
    audit_id: str,
) -> CopilotApprovalAuditRecord:
    """Return one approval audit record."""
    record = get_approval_audit_record(audit_id)

    if record is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"Approval audit record not found: {audit_id}",
        )

    return record


@app.post(
    "/copilot/decisions/{decision_id}/approval",
    response_model=CopilotDecisionApprovalResult,
)
def approve_copilot_decision(
    decision_id: str,
    request: CopilotDecisionApprovalRequest,
) -> CopilotDecisionApprovalResult:
    """Evaluate and audit human approval for a decision assessment."""
    return evaluate_decision_approval(
        decision_id=decision_id,
        assessment=request.assessment,
        approver=request.approver,
        approval_comment=request.approval_comment,
    )


@app.get(
    "/copilot/context/{conversation_id}",
    response_model=CopilotSessionSummary,
)
def get_copilot_context(
    conversation_id: str,
) -> CopilotSessionSummary:
    """Return an auditable summary of the Copilot conversation context."""
    return get_session_summary(conversation_id)

