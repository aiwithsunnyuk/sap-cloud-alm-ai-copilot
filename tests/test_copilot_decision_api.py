from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def _payload():
    return {
        "question": "What should we review before the deployment?",
        "intent": "deployment",
        "agent_results": [
            {
                "agent_id": "deployment-investigator",
                "orchestration": {
                    "skill_name": "Deployment Investigation",
                    "intent": "deployment",
                    "status": "success",
                    "tool_results": [
                        {
                            "tool_name": "get_deployment_summary",
                            "status": "success",
                            "summary": "DEP-001 was rolled back.",
                            "data": {
                                "findings": [
                                    "Deployment validation failed."
                                ],
                                "recommendations": [
                                    "Review deployment validation evidence."
                                ],
                            },
                            "evidence": [
                                "DEP-001: rollback completed"
                            ],
                            "source": "deployment service",
                            "trace": ["Tool Execution"],
                            "approval_required": False,
                        }
                    ],
                    "successful_tools": 1,
                    "blocked_tools": 0,
                    "failed_tools": 0,
                    "approval_required": False,
                    "trace": ["Tool Execution"],
                },
            },
            {
                "agent_id": "incident-investigator",
                "orchestration": {
                    "skill_name": "Incident Investigation",
                    "intent": "deployment",
                    "status": "success",
                    "tool_results": [
                        {
                            "tool_name": "get_incident_summary",
                            "status": "success",
                            "summary": "INC-003 is related.",
                            "data": {
                                "findings": [
                                    "Related incident remains open."
                                ],
                                "recommendations": [
                                    "Review incident corrective actions."
                                ],
                            },
                            "evidence": [
                                "INC-003: deployment-related incident"
                            ],
                            "source": "incident service",
                            "trace": ["Tool Execution"],
                            "approval_required": False,
                        }
                    ],
                    "successful_tools": 1,
                    "blocked_tools": 0,
                    "failed_tools": 0,
                    "approval_required": False,
                    "trace": ["Tool Execution"],
                },
            },
        ],
    }


def test_decision_api_returns_candidate_and_confidence():
    response = client.post(
        "/copilot/decisions",
        json=_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["status"] == "success"
    assert body["decision"]["decision"] == "review_recommendations"

    assert body["decision"]["contributing_agents"] == [
        "deployment-investigator",
        "incident-investigator",
    ]

    assert len(body["decision"]["evidence"]) == 2
    assert body["decision"]["action_required"] is True
    assert body["decision"]["approval_required"] is True

    assert body["confidence"]["score"] == 90
    assert body["confidence"]["level"] == "high"

    assert body["decision"]["trace"][-1] == "Decision Confidence"


def test_decision_api_handles_empty_agent_results():
    payload = {
        "question": "What should we review?",
        "intent": "decision_brief",
        "agent_results": [],
    }

    response = client.post(
        "/copilot/decisions",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["status"] == "insufficient_evidence"
    assert body["decision"]["decision"] == "insufficient_evidence"
    assert body["confidence"]["score"] == 0
    assert body["confidence"]["level"] == "none"


def test_decision_api_preserves_partial_failure():
    payload = _payload()

    payload["agent_results"][1]["orchestration"]["status"] = "partial_failure"
    payload["agent_results"][1]["orchestration"]["failed_tools"] = 1
    payload["agent_results"][1]["orchestration"]["successful_tools"] = 0

    response = client.post(
        "/copilot/decisions",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["status"] == "partial_failure"
    assert body["decision"]["decision"] == "review_partial_results"
    assert body["confidence"]["score"] == 65
    assert body["confidence"]["level"] == "medium"


def test_decision_api_rejects_invalid_intent():
    payload = _payload()
    payload["intent"] = "not-a-real-intent"

    response = client.post(
        "/copilot/decisions",
        json=payload,
    )

    assert response.status_code == 422


def test_decision_api_is_read_only_candidate_generation():
    response = client.post(
        "/copilot/decisions",
        json=_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"]["decision"] == "review_recommendations"
    assert body["decision"]["approval_required"] is True
