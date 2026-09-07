from pathlib import Path
import json

from fastapi import FastAPI, HTTPException

from app.services.risk_engine import calculate_risk_score

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


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "sap-cloud-alm-ai-copilot",
    }


@app.get("/projects")
def get_projects():
    return load_json("projects.json")


@app.get("/tasks")
def get_tasks():
    return load_json("tasks.json")


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


@app.get("/risks/summary")
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

@app.get("/workstreams/summary")
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
@app.get("/projects/{project_id}/summary")
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
