from fastapi.testclient import TestClient

from app.api import app
from app.models.copilot import CopilotIntent


client = TestClient(app)


def _orchestration(
    *,
    skill_name: str,
    tool_name: str,
    evidence: list[str],
    recommendations: list[str] | None = None,
    status: str = "success",
):
    from app.models.copilot_normalized_result import CopilotNormalizedResult
    from app.models.copilot_orchestration import CopilotOrchestrationResult

    normalized = CopilotNormalizedResult(
        tool_name=tool_name,
        status="success",
        summary=f"{skill_name} result",
        data={
            "findings": [],
            "recommendations": recommendations or [],
        },
        evidence=evidence,
        source=f"{skill_name} service",
        trace=["Tool Execution"],
        approval_required=False,
    )

    return CopilotOrchestrationResult(
        skill_name=skill_name,
        intent=CopilotIntent.DEPLOYMENT,
        status=status,
        tool_results=[normalized],
        successful_tools=1 if status == "success" else 0,
        blocked_tools=0,
        failed_tools=1 if status != "success" else 0,
        approval_required=False,
        trace=[
            "Skill Planning",
            "Tool Execution",
            "Normalized Tool Results",
        ],
    )


def test_decision_orchestration_api_returns_assessment():
    response = client.post(
        "/copilot/decisions/orchestrate",
        json={
            "question": "What should we review before deployment?",
            "intent": CopilotIntent.DEPLOYMENT.value,
            "agent_results": [
                {
                    "agent_id": "deployment-investigator",
                    "orchestration": _orchestration(
                        skill_name="Deployment Investigation",
                        tool_name="get_deployment_summary",
                        evidence=[
                            "DEP-001: rollback completed",
                            "DEP-001: validation failed",
                        ],
                        recommendations=[
                            "Review deployment validation."
                        ],
                    ).model_dump(mode="json"),
                },
                {
                    "agent_id": "incident-investigator",
                    "orchestration": _orchestration(
                        skill_name="Incident Investigation",
                        tool_name="get_incident_summary",
                        evidence=["INC-003: deployment incident"],
                        recommendations=[
                            "Review incident corrective actions."
                        ],
                    ).model_dump(mode="json"),
                },
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["status"] == "success"
    assert body["decision"]["decision"] == "review_recommendations"

    assert body["confidence"]["score"] == 100
    assert body["confidence"]["level"] == "high"

    assert body["review_required"] is False
    assert body["auditable"] is True

    assert body["trace"] == [
        "Multi-Agent Decision Orchestration",
        "Decision Candidate",
        "Decision Confidence",
        "Decision Assessment",
    ]


def test_decision_orchestration_api_handles_empty_agents():
    response = client.post(
        "/copilot/decisions/orchestrate",
        json={
            "question": "What should we review?",
            "intent": CopilotIntent.DECISION_BRIEF.value,
            "agent_results": [],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["status"] == "insufficient_evidence"
    assert body["decision"]["decision"] == "insufficient_evidence"

    assert body["confidence"]["score"] == 0
    assert body["confidence"]["level"] == "none"

    assert body["review_required"] is True


def test_decision_orchestration_api_handles_partial_failure():
    response = client.post(
        "/copilot/decisions/orchestrate",
        json={
            "question": "Investigate deployment",
            "intent": CopilotIntent.DEPLOYMENT.value,
            "agent_results": [
                {
                    "agent_id": "deployment-investigator",
                    "orchestration": _orchestration(
                        skill_name="Deployment Investigation",
                        tool_name="get_deployment_summary",
                        evidence=["DEP-001"],
                    ).model_dump(mode="json"),
                },
                {
                    "agent_id": "incident-investigator",
                    "orchestration": _orchestration(
                        skill_name="Incident Investigation",
                        tool_name="get_incident_summary",
                        evidence=[],
                        status="partial_failure",
                    ).model_dump(mode="json"),
                },
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["status"] == "partial_failure"

    # Two contributing agents still earn the multi-agent confidence bonus.
    assert body["confidence"]["score"] == 55
    assert body["confidence"]["level"] == "medium"

    assert body["review_required"] is False


def test_decision_orchestration_api_rejects_invalid_intent():
    response = client.post(
        "/copilot/decisions/orchestrate",
        json={
            "question": "Investigate deployment",
            "intent": "NOT_A_REAL_INTENT",
            "agent_results": [],
        },
    )

    assert response.status_code == 422
