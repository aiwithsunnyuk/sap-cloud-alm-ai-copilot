from app.models.copilot import CopilotIntent
from app.services.copilot_agent_selector import select_agent


def test_deployment_intent_selects_deployment_agent():
    result = select_agent(
        CopilotIntent.DEPLOYMENT
    )

    assert result.status == "selected"
    assert result.selected_agent_id == (
        "deployment-investigator"
    )
    assert result.selected_agent_name == (
        "Deployment Investigator"
    )
    assert result.candidate_agent_ids == [
        "deployment-investigator"
    ]


def test_incident_intent_selects_incident_agent():
    result = select_agent(
        CopilotIntent.INCIDENT
    )

    assert result.status == "selected"
    assert result.selected_agent_id == (
        "incident-investigator"
    )


def test_recommendation_selects_operations_decision_agent():
    result = select_agent(
        CopilotIntent.RECOMMENDATION
    )

    assert result.status == "selected"
    assert result.selected_agent_id == (
        "operations-decision"
    )


def test_explanation_without_entity_is_ambiguous():
    result = select_agent(
        CopilotIntent.EXPLANATION
    )

    assert result.status == "ambiguous"
    assert result.selected_agent_id is None
    assert set(result.candidate_agent_ids) == {
        "deployment-investigator",
        "incident-investigator",
        "release-governance",
    }


def test_explanation_with_deployment_context_selects_owner():
    result = select_agent(
        CopilotIntent.EXPLANATION,
        entity_type="deployment",
    )

    assert result.status == "selected"
    assert result.selected_agent_id == (
        "deployment-investigator"
    )
    assert result.entity_type == "deployment"


def test_unknown_intent_has_no_agent():
    result = select_agent(
        CopilotIntent.UNKNOWN
    )

    assert result.status == "none"
    assert result.selected_agent_id is None
    assert result.candidate_agent_ids == []
