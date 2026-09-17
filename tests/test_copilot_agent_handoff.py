from app.models.copilot import CopilotIntent
from app.services.copilot_agent_handoff import (
    request_agent_handoff,
)


def test_deployment_agent_can_handoff_to_incident_agent():
    result = request_agent_handoff(
        source_agent_id="deployment-investigator",
        target_intent=CopilotIntent.INCIDENT,
        entity_type="incident",
        entity_id="INC-003",
    )

    assert result.status == "allowed"
    assert result.source_agent_id == (
        "deployment-investigator"
    )
    assert result.target_agent_id == (
        "incident-investigator"
    )
    assert result.target_agent_name == (
        "Incident Investigator"
    )
    assert result.entity_id == "INC-003"
    assert result.approval_required is False
    assert "Handoff Allowed" in result.trace


def test_incident_agent_can_handoff_to_decision_agent():
    result = request_agent_handoff(
        source_agent_id="incident-investigator",
        target_intent=CopilotIntent.RECOMMENDATION,
    )

    assert result.status == "allowed"
    assert result.target_agent_id == (
        "operations-decision"
    )


def test_unauthorized_handoff_is_blocked():
    result = request_agent_handoff(
        source_agent_id="operations-decision",
        target_intent=CopilotIntent.DEPLOYMENT,
    )

    assert result.status == "blocked"
    assert result.target_agent_id is None


def test_unknown_source_agent_is_blocked():
    result = request_agent_handoff(
        source_agent_id="not-a-real-agent",
        target_intent=CopilotIntent.INCIDENT,
    )

    assert result.status == "blocked"
    assert "not registered" in result.reason.lower()


def test_ambiguous_target_is_not_guessed():
    result = request_agent_handoff(
        source_agent_id="deployment-investigator",
        target_intent=CopilotIntent.EXPLANATION,
    )

    assert result.status == "blocked"
    assert result.target_agent_id is None
