import json
from pathlib import Path
from typing import Any

from app.services.risk_engine import calculate_risk_score


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_json(filename: str) -> list[dict[str, Any]]:
    """Load a JSON dataset from the project's data directory."""

    file_path = DATA_DIR / filename

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_tasks() -> list[dict[str, Any]]:
    return load_json("tasks.json")


def get_dependencies() -> list[dict[str, Any]]:
    return load_json("dependencies.json")


def get_risks() -> list[dict[str, Any]]:
    return load_json("risks.json")


def get_task_risk(task_id: str) -> dict[str, Any] | None:
    tasks = get_tasks()
    dependencies = get_dependencies()
    risks = get_risks()

    for task in tasks:
        if task.get("task_id") == task_id:
            return calculate_risk_score(
                task=task,
                dependencies=dependencies,
                risks=risks,
            )

    return None


def get_all_task_risks() -> list[dict[str, Any]]:
    tasks = get_tasks()
    dependencies = get_dependencies()
    risks = get_risks()

    results = [
        calculate_risk_score(
            task=task,
            dependencies=dependencies,
            risks=risks,
        )
        for task in tasks
    ]

    return sorted(
        results,
        key=lambda item: item["risk_score"],
        reverse=True,
    )


def get_risk_summary() -> dict[str, Any]:
    """Return an executive-level summary of project task risks."""

    task_risks = get_all_task_risks()

    counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
    }

    for task in task_risks:
        risk_level = task["risk_level"]
        counts[risk_level] += 1

    top_risks = task_risks[:3]

    return {
        "project_id": "PRJ-001",
        "total_tasks": len(task_risks),
        "risk_distribution": counts,
        "top_risks": top_risks,
    }
