from fastapi.testclient import TestClient

from app.api import app
from app.models.copilot import CopilotIntent


client = TestClient(app)


def _payload(**overrides):
    payload = {
        "agent_id": "deployment-investigator",
        "intent": CopilotIntent.DEPLOYMENT.value,
        "trace": [
            "Agent Selection",
            "Skill Planning",
            "Governance",
            "Tool Execution",
            "Handoff",
        ],
    }
    payload.update(overrides)
    return payload


def test_agent_evaluation_api_passes_for_valid_execution():
    response = client.post(
        "/copilot/agents/evaluate",
        json=_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["agent_id"] == "deployment-investigator"
    assert body["intent"] == CopilotIntent.DEPLOYMENT.value
    assert body["status"] == "PASS"
    assert body["score"] == 100
    assert body["governance_compliant"] is True
    assert body["trace_complete"] is True
    assert body["trace"][-1] == "Evaluation"


def test_agent_evaluation_api_detects_incomplete_trace():
    response = client.post(
        "/copilot/agents/evaluate",
        json=_payload(
            trace=[
                "Agent Selection",
                "Skill Planning",
                "Governance",
                "Tool Execution",
            ]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "WARN"
    assert body["score"] == 90
    assert body["trace_complete"] is False
    assert any("trace is incomplete" in item for item in body["findings"])


def test_agent_evaluation_api_fails_execution():
    response = client.post(
        "/copilot/agents/evaluate",
        json=_payload(
            execution_successful=False,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "FAIL"
    assert body["score"] == 85
    assert body["execution_successful"] is False


def test_agent_evaluation_api_fails_unknown_agent():
    response = client.post(
        "/copilot/agents/evaluate",
        json=_payload(
            agent_id="unknown-agent",
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "FAIL"
    assert body["score"] == 0
    assert body["governance_compliant"] is False
    assert body["findings"] == ["Unknown agent: unknown-agent"]


def test_agent_evaluation_api_accepts_correctly_blocked_read_only_action():
    response = client.post(
        "/copilot/agents/evaluate",
        json=_payload(
            requested_action=True,
            approved=False,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "PASS"
    assert body["score"] == 100
    assert body["governance_compliant"] is True
