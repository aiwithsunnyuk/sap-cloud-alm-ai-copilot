from app.models.copilot import CopilotIntent
from app.services.copilot_agent_registry import (
    get_agent,
    get_agents_for_intent,
    get_all_agents,
)


def test_agent_registry_contains_specialized_agents():
    agents = get_all_agents()

    names = {
        agent.agent_id
        for agent in agents
    }

    assert names == {
        "deployment-investigator",
        "incident-investigator",
        "release-governance",
        "operations-decision",
    }

    assert len(agents) == 4


def test_deployment_agent_contract():
    agent = get_agent("deployment-investigator")

    assert agent is not None
    assert agent.name == "Deployment Investigator"
    assert CopilotIntent.DEPLOYMENT in agent.intents
    assert "Deployment Investigation" in agent.skills
    assert agent.read_only is True
    assert agent.approval_required is False


def test_incident_intent_discovers_incident_agent():
    agents = get_agents_for_intent(
        CopilotIntent.INCIDENT
    )

    assert len(agents) == 1
    assert agents[0].agent_id == (
        "incident-investigator"
    )


def test_recommendation_intent_discovers_decision_agent():
    agents = get_agents_for_intent(
        CopilotIntent.RECOMMENDATION
    )

    assert len(agents) == 1
    assert agents[0].agent_id == (
        "operations-decision"
    )


def test_unknown_intent_has_no_agent():
    agents = get_agents_for_intent(
        CopilotIntent.UNKNOWN
    )

    assert agents == []
