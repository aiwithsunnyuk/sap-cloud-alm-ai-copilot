from fastapi import FastAPI, HTTPException

from app.config import APP_NAME, APP_VERSION
from app.services.project_service import (
    get_all_task_risks,
    get_risk_summary,
    get_task_risk,
)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


@app.get("/")
def root():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/api/v1/risks")
def get_risks():
    """Return all project tasks ranked by calculated risk."""

    risks = get_all_task_risks()

    return {
        "count": len(risks),
        "risks": risks,
    }


@app.get("/api/v1/risks/{task_id}")
def get_risk(task_id: str):
    """Return calculated risk for a specific task."""

    result = get_task_risk(task_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_id}' not found",
        )

    return result


@app.get("/api/v1/risk-summary")
def risk_summary():
    """Return an executive summary of project risks."""

    return get_risk_summary()
