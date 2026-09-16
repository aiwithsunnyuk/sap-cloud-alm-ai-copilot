from typing import Any

from app.services.historical_risk import get_task_history


def calculate_risk_trend(task_id: str) -> dict[str, Any]:
    """Calculate historical risk trend for a task."""

    history = get_task_history(task_id)

    if not history:
        return {
            "task_id": task_id,
            "snapshot_count": 0,
            "starting_risk_score": None,
            "current_risk_score": None,
            "risk_change": None,
            "risk_velocity": None,
            "trend": "No Data",
            "severity_transition": None,
        }

    starting_score = history[0]["risk_score"]
    current_score = history[-1]["risk_score"]

    risk_change = current_score - starting_score

    intervals = len(history) - 1

    if intervals > 0:
        risk_velocity = round(risk_change / intervals, 2)
    else:
        risk_velocity = 0.0

    if risk_change >= 5:
        trend = "Deteriorating"
    elif risk_change <= -5:
        trend = "Improving"
    else:
        trend = "Stable"

    starting_level = history[0]["risk_level"]
    current_level = history[-1]["risk_level"]

    if starting_level == current_level:
        severity_transition = current_level
    else:
        severity_transition = f"{starting_level} → {current_level}"

    return {
        "task_id": task_id,
        "snapshot_count": len(history),
        "starting_risk_score": starting_score,
        "current_risk_score": current_score,
        "risk_change": risk_change,
        "risk_velocity": risk_velocity,
        "trend": trend,
        "severity_transition": severity_transition,
    }
