import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def generate_early_warnings() -> dict:
    """
    Generate early-warning indicators from project tasks,
    risks and dependencies.
    """

    tasks = load_json("tasks.json")
    risks = load_json("risks.json")
    dependencies = load_json("dependencies.json")

    warnings = []
    affected_tasks = {}

    # ---------------------------------------------------------
    # Task-level risk warnings
    # ---------------------------------------------------------

    for task in tasks:
        task_id = task.get("task_id", "UNKNOWN")
        task_name = task.get("task_name", "Unnamed task")

        risk_score = task.get("risk_score")

        if risk_score is None:
            continue

        try:
            risk_score = float(risk_score)
        except (TypeError, ValueError):
            continue

        if risk_score >= 75:
            severity = "Critical"
        elif risk_score >= 50:
            severity = "High"
        elif risk_score >= 30:
            severity = "Medium"
        else:
            severity = "Low"

        if risk_score >= 75:
            warnings.append(
                {
                    "warning_type": "HIGH_TASK_RISK",
                    "severity": severity,
                    "task_id": task_id,
                    "task_name": task_name,
                    "risk_score": risk_score,
                    "message": (
                        f"Task {task_id} ({task_name}) has a "
                        f"critical risk score of {risk_score}."
                    ),
                    "recommended_action": (
                        "Review the task immediately with the "
                        "responsible owner and establish a recovery plan."
                    ),
                }
            )

        elif risk_score >= 50:
            warnings.append(
                {
                    "warning_type": "ELEVATED_TASK_RISK",
                    "severity": severity,
                    "task_id": task_id,
                    "task_name": task_name,
                    "risk_score": risk_score,
                    "message": (
                        f"Task {task_id} ({task_name}) has an "
                        f"elevated risk score of {risk_score}."
                    ),
                    "recommended_action": (
                        "Review mitigation actions and monitor the "
                        "task closely."
                    ),
                }
            )

    # ---------------------------------------------------------
    # Risk register warnings
    # ---------------------------------------------------------

    for risk in risks:
        risk_id = risk.get("risk_id", "UNKNOWN")
        title = risk.get("title", "Unnamed risk")
        severity = risk.get("severity", "Low")
        status = risk.get("status", "Unknown")
        workstream_id = risk.get("workstream_id")

        if status != "Open":
            continue

        if severity == "Critical":
            warnings.append(
                {
                    "warning_type": "OPEN_CRITICAL_RISK",
                    "severity": "Critical",
                    "risk_id": risk_id,
                    "workstream_id": workstream_id,
                    "title": title,
                    "message": (
                        f"Open critical risk {risk_id}: {title}."
                    ),
                    "recommended_action": risk.get(
                        "mitigation",
                        "Escalate and establish an immediate recovery plan.",
                    ),
                }
            )

        elif severity == "High":
            warnings.append(
                {
                    "warning_type": "OPEN_HIGH_RISK",
                    "severity": "High",
                    "risk_id": risk_id,
                    "workstream_id": workstream_id,
                    "title": title,
                    "message": (
                        f"Open high risk {risk_id}: {title}."
                    ),
                    "recommended_action": risk.get(
                        "mitigation",
                        "Review mitigation progress with the risk owner.",
                    ),
                }
            )

    # ---------------------------------------------------------
    # Dependency warnings
    # ---------------------------------------------------------

    task_lookup = {
        task.get("task_id"): task
        for task in tasks
        if task.get("task_id")
    }

    for dependency in dependencies:
        status = dependency.get("status")

        if status != "Open":
            continue

        from_task = dependency.get("from_task")
        to_task = dependency.get("to_task")
        dependency_type = dependency.get("type", "Unknown")

        source_task = task_lookup.get(from_task, {})
        target_task = task_lookup.get(to_task, {})

        source_name = source_task.get("task_name", from_task)
        target_name = target_task.get("task_name", to_task)

        if dependency_type == "Blocks":
            affected_tasks.setdefault(
                to_task,
                {
                    "task_id": to_task,
                    "task_name": target_name,
                    "blocked_by": [],
                },
            )

            affected_tasks[to_task]["blocked_by"].append(
                {
                    "dependency_id": dependency.get("dependency_id"),
                    "blocking_task": from_task,
                    "blocking_task_name": source_name,
                }
            )

            warnings.append(
                {
                    "warning_type": "OPEN_BLOCKING_DEPENDENCY",
                    "severity": "High",
                    "dependency_id": dependency.get("dependency_id"),
                    "blocking_task": from_task,
                    "blocking_task_name": source_name,
                    "affected_task": to_task,
                    "affected_task_name": target_name,
                    "message": (
                        f"{source_name} is blocking {target_name}."
                    ),
                    "recommended_action": (
                        "Resolve the blocking dependency before "
                        "downstream delivery is impacted."
                    ),
                }
            )

    # ---------------------------------------------------------
    # Determine overall warning level
    # ---------------------------------------------------------

    critical_count = sum(
        1
        for warning in warnings
        if warning.get("severity") == "Critical"
    )

    high_count = sum(
        1
        for warning in warnings
        if warning.get("severity") == "High"
    )

    if critical_count > 0:
        overall_status = "Critical"
    elif high_count > 0:
        overall_status = "High"
    elif warnings:
        overall_status = "Medium"
    else:
        overall_status = "Green"

    # ---------------------------------------------------------
    # Executive recommendation
    # ---------------------------------------------------------

    if overall_status == "Critical":
        executive_action = (
            "Immediate management attention required. "
            "Prioritize critical risks and remove blocking dependencies."
        )
    elif overall_status == "High":
        executive_action = (
            "Elevated delivery risk detected. "
            "Review high-risk tasks and open dependencies."
        )
    elif overall_status == "Medium":
        executive_action = (
            "Monitor emerging risks and confirm mitigation actions."
        )
    else:
        executive_action = (
            "No significant early-warning indicators detected."
        )

    return {
        "overall_status": overall_status,
        "total_warnings": len(warnings),
        "critical_warnings": critical_count,
        "high_warnings": high_count,
        "affected_tasks": list(affected_tasks.values()),
        "executive_action": executive_action,
        "warnings": warnings,
    }
