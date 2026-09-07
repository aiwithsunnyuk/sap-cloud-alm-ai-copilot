"""
Health explanation service for SAP Cloud ALM AI Copilot.

This module converts calculated project/workstream health metrics
into concise, deterministic explanations.

No external AI/LLM dependency is required at this stage.
The rule-based implementation gives us a stable foundation that
can later be replaced or augmented with an LLM/agent.
"""


def _safe_int(value, default=0):
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def explain_project_health(summary: dict) -> dict:
    """
    Generate a structured explanation for a project/workstream health summary.

    Expected input:

    {
        "workstream_id": "WS-INT",
        "total_tasks": 2,
        "critical": 1,
        "high": 1,
        "medium": 0,
        "low": 0,
        "average_risk_score": 85.0,
        "blocked_tasks": 1,
        "highest_risk_task": {
            "task_id": "TASK-006",
            "task_name": "Complete API Integration Testing",
            "risk_score": 100,
            "risk_level": "Critical"
        },
        "overall_health": "Red"
    }

    Returns:

    {
        "health_explanation": "...",
        "key_drivers": [...],
        "recommended_actions": [...]
    }
    """

    if not isinstance(summary, dict):
        return {
            "health_explanation": "Health information is unavailable.",
            "key_drivers": [],
            "recommended_actions": [],
        }

    workstream_id = summary.get("workstream_id", "UNKNOWN")
    overall_health = str(
        summary.get("overall_health", "Unknown")
    ).strip().title()

    total_tasks = _safe_int(summary.get("total_tasks"))
    critical = _safe_int(summary.get("critical"))
    high = _safe_int(summary.get("high"))
    medium = _safe_int(summary.get("medium"))
    low = _safe_int(summary.get("low"))
    blocked_tasks = _safe_int(summary.get("blocked_tasks"))

    average_risk_score = _safe_float(
        summary.get("average_risk_score")
    )

    highest_risk_task = summary.get("highest_risk_task") or {}

    highest_risk_task_id = highest_risk_task.get("task_id")
    highest_risk_task_name = highest_risk_task.get(
        "task_name",
        "Unknown task",
    )
    highest_risk_score = _safe_float(
        highest_risk_task.get("risk_score")
    )
    highest_risk_level = str(
        highest_risk_task.get("risk_level", "Unknown")
    ).strip().title()

    key_drivers = []
    recommended_actions = []

    # ---------------------------------------------------------
    # Overall health explanation
    # ---------------------------------------------------------

    if overall_health == "Red":
        health_explanation = (
            f"Workstream {workstream_id} is in Red health. "
            f"The workstream has {critical} critical risk"
            f"{'s' if critical != 1 else ''}"
            f" and {blocked_tasks} blocked task"
            f"{'s' if blocked_tasks != 1 else ''}. "
            f"The average risk score is {average_risk_score:.1f}, "
            "indicating significant delivery risk."
        )

    elif overall_health == "Amber":
        health_explanation = (
            f"Workstream {workstream_id} is in Amber health. "
            f"The workstream has {high} high-risk task"
            f"{'s' if high != 1 else ''}"
            f" and {blocked_tasks} blocked task"
            f"{'s' if blocked_tasks != 1 else ''}. "
            f"The average risk score is {average_risk_score:.1f}, "
            "indicating that management attention is required."
        )

    elif overall_health == "Green":
        health_explanation = (
            f"Workstream {workstream_id} is in Green health. "
            f"The workstream contains {total_tasks} task"
            f"{'s' if total_tasks != 1 else ''} with no critical "
            "risk currently identified. Delivery appears stable "
            f"with an average risk score of {average_risk_score:.1f}."
        )

    else:
        health_explanation = (
            f"Workstream {workstream_id} has an overall health status "
            f"of {overall_health}. Further assessment may be required."
        )

    # ---------------------------------------------------------
    # Key risk drivers
    # ---------------------------------------------------------

    if critical > 0:
        key_drivers.append(
            f"{critical} critical-risk task"
            f"{'s' if critical != 1 else ''} identified."
        )

    if high > 0:
        key_drivers.append(
            f"{high} high-risk task"
            f"{'s' if high != 1 else ''} identified."
        )

    if blocked_tasks > 0:
        key_drivers.append(
            f"{blocked_tasks} task"
            f"{'s' if blocked_tasks != 1 else ''} currently blocked."
        )

    if highest_risk_task_id:
        key_drivers.append(
            f"Highest-risk task is {highest_risk_task_id} "
            f"({highest_risk_task_name}) with a risk score of "
            f"{highest_risk_score:.0f} ({highest_risk_level})."
        )

    if average_risk_score >= 80:
        key_drivers.append(
            f"Average risk score of {average_risk_score:.1f} "
            "is very high."
        )

    elif average_risk_score >= 50:
        key_drivers.append(
            f"Average risk score of {average_risk_score:.1f} "
            "indicates elevated delivery risk."
        )

    # ---------------------------------------------------------
    # Recommended actions
    # ---------------------------------------------------------

    if critical > 0:
        recommended_actions.append(
            "Prioritize critical-risk tasks immediately."
        )

    if blocked_tasks > 0:
        recommended_actions.append(
            "Resolve blocking issues and dependencies before "
            "downstream delivery is impacted."
        )

    if highest_risk_task_id:
        recommended_actions.append(
            f"Review {highest_risk_task_id} ({highest_risk_task_name}) "
            "with the responsible owner and establish a recovery plan."
        )

    if high > 0:
        recommended_actions.append(
            "Review high-risk tasks frequently and confirm mitigation "
            "actions with task owners."
        )

    if average_risk_score >= 80:
        recommended_actions.append(
            "Escalate the workstream for management review because "
            "the overall risk exposure is high."
        )

    elif average_risk_score >= 50:
        recommended_actions.append(
            "Monitor risk trends closely and verify that mitigation "
            "actions are progressing."
        )

    if not recommended_actions:
        recommended_actions.append(
            "Continue monitoring task progress and risk indicators."
        )

    # ---------------------------------------------------------
    # Final structured response
    # ---------------------------------------------------------

    return {
        "health_explanation": health_explanation,
        "key_drivers": key_drivers,
        "recommended_actions": recommended_actions,
    }
