from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def _tool_result(
    tool_name,
    summary,
    evidence,
    findings,
    recommendations,
):
    return {
        "tool_name": tool_name,
        "status": "success",
        "summary": summary,
        "data": {
            "findings": findings,
            "recommendations": recommendations,
        },
        "evidence": evidence,
        "source": "synthetic SAP Cloud ALM intelligence",
        "trace": ["Tool Execution"],
        "approval_required": False,
    }


def _orchestration(
    skill_name,
    tool_result,
):
    return {
        "skill_name": skill_name,
        "intent": "deployment",
        "status": "success",
        "tool_results": [tool_result],
        "successful_tools": 1,
        "blocked_tools": 0,
        "failed_tools": 0,
        "approval_required": False,
        "trace": [
            "Skill Planning",
            "Tool Execution",
            "Normalized Tool Results",
        ],
    }


def test_operational_decision_end_to_end():
    payload = {
        "question": (
            "What should we review before proceeding with the "
            "production deployment?"
        ),
        "intent": "deployment",
        "agent_results": [
            {
                "agent_id": "deployment-investigator",
                "orchestration": _orchestration(
                    "Deployment Investigation",
                    _tool_result(
                        "get_deployment_summary",
                        "DEP-001 was rolled back after validation failure.",
                        [
                            "DEP-001: rollback completed",
                            "DEP-001: validation failed",
                        ],
                        [
                            "Production deployment validation failed."
                        ],
                        [
                            "Review deployment validation evidence."
                        ],
                    ),
                ),
            },
            {
                "agent_id": "incident-investigator",
                "orchestration": _orchestration(
                    "Incident Investigation",
                    _tool_result(
                        "get_incident_summary",
                        "INC-003 is associated with the deployment issue.",
                        [
                            "INC-003: deployment-related incident",
                            "PRB-001: root cause investigation",
                        ],
                        [
                            "Related incident and problem remain operationally relevant."
                        ],
                        [
                            "Review incident corrective actions."
                        ],
                    ),
                ),
            },
            {
                "agent_id": "release-governance",
                "orchestration": _orchestration(
                    "Release Investigation",
                    _tool_result(
                        "get_release_summary",
                        "REL-001 requires governance review.",
                        [
                            "REL-001: planned production release",
                            "CHG-001: pending approval",
                        ],
                        [
                            "Production release has unresolved governance dependency."
                        ],
                        [
                            "Review release readiness and pending approval."
                        ],
                    ),
                ),
            },
        ],
    }

    response = client.post(
        "/copilot/decisions",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    decision = body["decision"]
    confidence = body["confidence"]

    assert decision["status"] == "success"
    assert decision["decision"] == "review_recommendations"

    assert decision["contributing_agents"] == [
        "deployment-investigator",
        "incident-investigator",
        "release-governance",
    ]

    assert len(decision["evidence"]) == 6
    assert len(decision["findings"]) == 3
    assert len(decision["recommendations"]) == 3

    assert decision["action_required"] is True
    assert decision["approval_required"] is True

    assert confidence["score"] == 100
    assert confidence["level"] == "high"

    assert decision["trace"] == [
        "Multi-Agent Decision Orchestration",
        "Decision Request",
        "Agent Contributions",
        "Evidence Aggregation",
        "Decision Candidate",
        "Decision Confidence",
    ]


def test_operational_decision_remains_uncertain_without_evidence():
    payload = {
        "question": "Should we proceed with the production deployment?",
        "intent": "deployment",
        "agent_results": [
            {
                "agent_id": "deployment-investigator",
                "orchestration": _orchestration(
                    "Deployment Investigation",
                    _tool_result(
                        "get_deployment_summary",
                        "Deployment check completed.",
                        [],
                        [],
                        [],
                    ),
                ),
            },
            {
                "agent_id": "incident-investigator",
                "orchestration": _orchestration(
                    "Incident Investigation",
                    _tool_result(
                        "get_incident_summary",
                        "Incident check completed.",
                        [],
                        [],
                        [],
                    ),
                ),
            },
        ],
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

    assert body["decision"]["action_required"] is False
    assert body["decision"]["approval_required"] is False
