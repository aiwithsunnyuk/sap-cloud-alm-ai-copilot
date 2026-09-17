from app.models.copilot import CopilotIntent
from app.services.copilot_agent_skill_planner import (
    build_agent_skill_plan,
)


def test_deployment_agent_gets_deployment_skill():
    plan = build_agent_skill_plan(
        agent_id="deployment-investigator",
        intent=CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    assert plan is not None
    assert plan.agent_id == "deployment-investigator"
    assert plan.agent_name == "Deployment Investigator"
    assert plan.intent == CopilotIntent.DEPLOYMENT
    assert plan.skill.skill_name == "Deployment Investigation"
    assert plan.skill.tools
    assert (
        plan.skill.tools[0].capability_name
        == "get_deployment_summary"
    )


def test_incident_agent_gets_incident_skill():
    plan = build_agent_skill_plan(
        agent_id="incident-investigator",
        intent=CopilotIntent.INCIDENT,
        entity_type="incident",
        entity_id="INC-003",
    )

    assert plan is not None
    assert plan.agent_id == "incident-investigator"
    assert plan.skill.skill_name == "Incident Investigation"

    tool_names = {
        tool.capability_name
        for tool in plan.skill.tools
    }

    assert "get_incident_summary" in tool_names


def test_operations_agent_gets_recommendation_skill():
    plan = build_agent_skill_plan(
        agent_id="operations-decision",
        intent=CopilotIntent.RECOMMENDATION,
    )

    assert plan is not None
    assert plan.skill.skill_name == "Recommendation Review"
    assert len(plan.skill.tools) == 1
    assert (
        plan.skill.tools[0].capability_name
        == "get_operational_recommendations"
    )


def test_agent_cannot_receive_unsupported_intent():
    plan = build_agent_skill_plan(
        agent_id="incident-investigator",
        intent=CopilotIntent.DEPLOYMENT,
    )

    assert plan is None


def test_missing_agent_returns_none():
    plan = build_agent_skill_plan(
        agent_id="not-a-real-agent",
        intent=CopilotIntent.DEPLOYMENT,
    )

    assert plan is None
