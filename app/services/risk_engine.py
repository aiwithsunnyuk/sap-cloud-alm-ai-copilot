from datetime import date
from typing import Any


PRIORITY_SCORES = {
    "Critical": 30,
    "High": 20,
    "Medium": 10,
    "Low": 5,
}

STATUS_SCORES = {
    "Blocked": 30,
    "Delayed": 25,
    "In Progress": 10,
    "Not Started": 5,
    "Completed": 0,
}


def calculate_risk_score(
    task: dict[str, Any],
    dependencies: list[dict[str, Any]],
    risks: list[dict[str, Any]],
    as_of_date: date | None = None,
) -> dict[str, Any]:
    """
    Calculate a deterministic risk score for a project task.

    The score combines:
    - task priority
    - task status
    - completion percentage
    - overdue status
    - blocking dependencies
    - related project risks
    """

    if as_of_date is None:
        as_of_date = date.today()

    score = 0
    reasons = []
    recommendations = []

    priority = task.get("priority", "Low")
    status = task.get("status", "Not Started")
    completion = task.get("percent_complete", 0)

    # Priority
    priority_score = PRIORITY_SCORES.get(priority, 0)
    score += priority_score

    if priority in ("Critical", "High"):
        reasons.append(f"{priority} priority task")

    # Status
    status_score = STATUS_SCORES.get(status, 0)
    score += status_score

    if status == "Blocked":
        reasons.append("Task is currently blocked")
        recommendations.append("Resolve the blocking issue immediately.")
    elif status == "Delayed":
        reasons.append("Task is delayed")
        recommendations.append("Review recovery actions and revised timeline.")

    # Completion
    if completion < 30:
        score += 20
        reasons.append(f"Low completion progress ({completion}%)")
    elif completion < 60:
        score += 10
        reasons.append(f"Task is only {completion}% complete")

    # Overdue
    planned_end = task.get("planned_end")

    if planned_end:
        end_date = date.fromisoformat(planned_end)

        if end_date < as_of_date and status != "Completed":
            score += 25
            reasons.append(f"Task is overdue since {planned_end}")
            recommendations.append("Escalate the task and establish a recovery plan.")

    # Dependencies
    task_id = task.get("task_id")

    blocking_dependencies = [
        dependency
        for dependency in dependencies
        if dependency.get("to_task") == task_id
        and dependency.get("type") == "Blocks"
        and dependency.get("status") == "Open"
    ]

    if blocking_dependencies:
        score += 15
        reasons.append(
            f"{len(blocking_dependencies)} open blocking dependency"
            + ("s" if len(blocking_dependencies) > 1 else "")
        )
        recommendations.append(
            "Resolve open dependencies before the downstream task is impacted."
        )

    # Related project risks
    workstream_id = task.get("workstream_id")

    related_risks = [
        risk
        for risk in risks
        if risk.get("workstream_id") == workstream_id
        and risk.get("status") == "Open"
    ]

    for risk in related_risks:
        severity = risk.get("severity", "Low")

        if severity == "Critical":
            score += 20
            reasons.append(f"Related critical risk: {risk.get('title')}")
        elif severity == "High":
            score += 15
            reasons.append(f"Related high risk: {risk.get('title')}")
        elif severity == "Medium":
            score += 8
            reasons.append(f"Related medium risk: {risk.get('title')}")

    # Cap score
    score = min(score, 100)

    # Risk classification
    if score >= 75:
        risk_level = "Critical"
    elif score >= 50:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not recommendations:
        recommendations.append("Continue monitoring task progress.")

    return {
        "task_id": task_id,
        "task_name": task.get("name"),
        "workstream_id": workstream_id,
        "owner": task.get("owner"),
        "priority": priority,
        "status": status,
        "completion": completion,
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendations": recommendations,
    }
