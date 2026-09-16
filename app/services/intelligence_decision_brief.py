from app.models.intelligence_decision_brief import DecisionBriefResponse
from app.services.intelligence_recommendation import (
    generate_operational_recommendations,
)
from app.services.operations_control_tower import (
    calculate_operations_control_tower,
)


def generate_operational_decision_brief() -> DecisionBriefResponse:
    recommendation_result = generate_operational_recommendations()
    control_tower = calculate_operations_control_tower()

    recommendations = recommendation_result.recommendations

    top_risks = [
        (
            f"{item.priority}: {item.title}"
        )
        for item in recommendations
    ]

    priority_actions = [
        item.action
        for item in recommendations
        if item.priority in {"P1", "P2"}
    ]

    affected_components = sorted(
        set(control_tower.get("affected_components", []))
    )

    affected_workstreams = sorted(
        set(control_tower.get("affected_workstreams", []))
    )

    decision_points: list[str] = []

    if recommendation_result.p1_recommendations > 0:
        decision_points.append(
            "Review P1 operational risks before approving further "
            "implementation or deployment activity."
        )

    if control_tower["changes"]["pending_approval"] > 0:
        decision_points.append(
            "Review pending change approval before implementation "
            "progresses."
        )

    if control_tower["deployments"]["rolled_back_deployments"] > 0:
        decision_points.append(
            "Review rollback evidence and corrective actions before "
            "repeating affected deployment activity."
        )

    if control_tower["problems"]["unresolved_root_causes"] > 0:
        decision_points.append(
            "Determine whether unresolved RCA work requires additional "
            "containment or corrective action."
        )

    if not decision_points:
        decision_points.append(
            "Continue operational monitoring and governance review."
        )

    executive_summary = (
        f"Current operational status is "
        f"{recommendation_result.overall_status} with "
        f"{recommendation_result.total_recommendations} prioritized "
        "recommendation(s). "
    )

    if recommendation_result.p1_recommendations > 0:
        executive_summary += (
            f"{recommendation_result.p1_recommendations} P1 issue(s) "
            "require immediate operational review."
        )
    else:
        executive_summary += (
            "No P1 recommendations are currently present."
        )

    evidence = [
        (
            f"Active alerts: "
            f"{control_tower['monitoring']['active_alerts']}"
        ),
        (
            f"Open incidents: "
            f"{control_tower['incidents']['open_incidents']}"
        ),
        (
            f"Active problems: "
            f"{control_tower['problems']['active_problems']}"
        ),
        (
            f"Pending change approvals: "
            f"{control_tower['changes']['pending_approval']}"
        ),
        (
            f"Rolled-back deployments: "
            f"{control_tower['deployments']['rolled_back_deployments']}"
        ),
        (
            f"Failed validations: "
            f"{control_tower['deployments']['failed_validations']}"
        ),
    ]

    return DecisionBriefResponse(
        brief_id="BRIEF-001",
        overall_status=recommendation_result.overall_status,
        executive_summary=executive_summary,
        total_risks=len(top_risks),
        priority_actions_count=len(priority_actions),
        top_risks=top_risks,
        priority_actions=priority_actions,
        affected_components=affected_components,
        affected_workstreams=affected_workstreams,
        decision_points=decision_points,
        evidence=evidence,
    )
