from datetime import date
from typing import Any

from app.models.domain import RiskLevel


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

    if as_of_date is None:
        as_of_date = date.today()

    score = 0
    reasons: list[str] = []
    recommendations: list[str] = []

    task_id = task.get("task_id")
    task_name = task.get("name")
    workstream_id = task.get("workstream_id")

    priority = task.get("priority", "Low")
    status = task.get("status", "Not Started")
    completion = task.get("percent_complete", 0)

    # Priority
    score += PRIORITY_SCORES.get(priority, 0)

    if priority in ("Critical", "High"):
        reasons.append(f"Task priority is {priority}.")
        recommendations.append(
            "Prioritize this task and review delivery progress frequently."
        )

    # Status
    score += STATUS_SCORES.get(status, 0)

    if status == "Blocked":
        reasons.append("Task is currently blocked.")
        recommendations.append(
            "Resolve the blocking issue immediately."
        )

    elif status == "Delayed":
        reasons.append("Task is currently delayed.")
        recommendations.append(
            "Review the delivery plan and establish a recovery plan."
        )

    # Completion
    try:
        completion = int(completion)
    except (TypeError, ValueError):
        completion = 0

    completion = max(0, min(completion, 100))

    if status != "Completed":

        if completion == 0:
            score += 10
            reasons.append("Task has no recorded completion progress.")
            recommendations.append(
                "Confirm task ownership and begin execution."
            )

        elif completion < 25:
            score += 8
            reasons.append(
                f"Task is only {completion}% complete."
            )
            recommendations.append(
                "Increase execution focus and review the remaining work."
            )

        elif completion < 50:
            score += 5
            reasons.append(
                f"Task is only {completion}% complete."
            )

    # Overdue
    planned_end = task.get("planned_end")

    if planned_end:

        try:
            if isinstance(planned_end, date):
                end_date = planned_end
            else:
                end_date = date.fromisoformat(str(planned_end))

            if end_date < as_of_date and status != "Completed":
                score += 25
                reasons.append(
                    f"Task is overdue since {planned_end}."
                )
                recommendations.append(
                    "Escalate the task and establish a recovery plan."
                )

        except (TypeError, ValueError):
            pass

    # Blocking dependencies
    blocking_dependencies = [
        dependency
        for dependency in dependencies
        if dependency.get("to_task") == task_id
        and dependency.get("type") == "Blocks"
        and dependency.get("status") == "Open"
    ]

    if blocking_dependencies:

        score += 15

        count = len(blocking_dependencies)

        if count == 1:
            reasons.append("1 open blocking dependency.")
        else:
            reasons.append(
                f"{count} open blocking dependencies."
            )

        recommendations.append(
            "Resolve open dependencies before the downstream task is impacted."
        )

    # Related project risks
    related_risks = [
        risk
        for risk in risks
        if risk.get("workstream_id") == workstream_id
        and risk.get("status") == "Open"
    ]

    for risk in related_risks:

        severity = risk.get("severity", "Low")
        title = risk.get("title", "Unnamed risk")

        if severity == "Critical":
            score += 20
            reasons.append(
                f"Related critical risk: {title}"
            )

        elif severity == "High":
            score += 15
            reasons.append(
                f"Related high risk: {title}"
            )

        elif severity == "Medium":
            score += 8
            reasons.append(
                f"Related medium risk: {title}"
            )

    # Cap score
    score = min(score, 100)

    # Risk classification
    if score >= 75:
        risk_level = RiskLevel.CRITICAL.value

    elif score >= 50:
        risk_level = RiskLevel.HIGH.value

    elif score >= 30:
        risk_level = RiskLevel.MEDIUM.value

    else:
        risk_level = RiskLevel.LOW.value

    # Default recommendation
    if not recommendations:
        recommendations.append(
            "Continue monitoring task progress."
        )

    return {
        "task_id": task_id,
        "task_name": task_name,
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
