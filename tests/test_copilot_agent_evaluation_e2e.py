from fastapi.testclient import TestClient

from app.models.copilot import CopilotIntent

from app.api import app


client = TestClient(app)


def test_deployment_investigator_end_to_end_evaluation():
    response = client.post(
        "/copilot/agents/evaluate",
        json={
            "agent_id": "deployment-investigator",
            "intent": CopilotIntent.DEPLOYMENT.value,
            "requested_action": False,
            "approved": False,
            "skill_plan_valid": True,
            "handoff_valid": True,
            "execution_successful": True,
            "grounded": True,
            "trace": [
                "Agent Selection",
                "Skill Planning",
                "Governance",
                "Tool Execution",
                "Handoff",
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["agent_id"] == "deployment-investigator"
    assert body["intent"] == CopilotIntent.DEPLOYMENT.value

    assert body["status"] == "PASS"
    assert body["score"] == 100

    assert body["governance_compliant"] is True
    assert body["skill_plan_valid"] is True
    assert body["handoff_valid"] is True
    assert body["execution_successful"] is True
    assert body["grounded"] is True
    assert body["trace_complete"] is True

    assert body["findings"] == []

    assert body["trace"] == [
        "Agent Selection",
        "Skill Planning",
        "Governance",
        "Tool Execution",
        "Handoff",
        "Evaluation",
    ]


def test_end_to_end_evaluation_detects_execution_failure():
    response = client.post(
        "/copilot/agents/evaluate",
        json={
            "agent_id": "deployment-investigator",
            "intent": CopilotIntent.DEPLOYMENT.value,
            "execution_successful": False,
            "grounded": True,
            "skill_plan_valid": True,
            "handoff_valid": True,
            "trace": [
                "Agent Selection",
                "Skill Planning",
                "Governance",
                "Tool Execution",
                "Handoff",
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "FAIL"
    assert body["execution_successful"] is False
    assert body["governance_compliant"] is True
    assert any(
        "execution did not complete successfully" in finding
        for finding in body["findings"]
    )


def test_end_to_end_evaluation_detects_governance_failure():
    response = client.post(
        "/copilot/agents/evaluate",
        json={
            "agent_id": "deployment-investigator",
            "intent": CopilotIntent.DEPLOYMENT.value,
            "requested_action": True,
            "approved": False,
            "skill_plan_valid": True,
            "handoff_valid": True,
            "execution_successful": True,
            "grounded": True,
            "trace": [
                "Agent Selection",
                "Skill Planning",
                "Governance",
                "Tool Execution",
                "Handoff",
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "PASS"
    assert body["governance_compliant"] is True
    assert body["score"] == 100
