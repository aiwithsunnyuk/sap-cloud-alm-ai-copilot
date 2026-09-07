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
