from app.models.copilot import CopilotIntent
from app.services.copilot_skill_planner import build_skill_plan


def test_deployment_skill_maps_to_multiple_tools():
    plan = build_skill_plan(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    assert plan is not None
    assert plan.skill_name == "Deployment Investigation"
    assert plan.intent == CopilotIntent.DEPLOYMENT
    assert plan.primary_tool == "get_deployment_summary"
    assert plan.read_only is True
    assert plan.approval_required is False

    tool_names = {
        tool.capability_name
        for tool in plan.tools
    }

    assert tool_names == {
        "get_deployment_summary",
        "get_operational_correlations",
        "get_operational_recommendations",
    }

    for tool in plan.tools:
        assert tool.entity_type == "deployment"
        assert tool.entity_id == "DEP-001"


def test_incident_skill_maps_to_investigation_tools():
    plan = build_skill_plan(
        CopilotIntent.INCIDENT,
        entity_type="incident",
        entity_id="INC-003",
    )

    assert plan is not None

    tool_names = {
        tool.capability_name
        for tool in plan.tools
    }

    assert "get_incident_summary" in tool_names
    assert "get_operational_correlations" in tool_names
    assert "get_operational_recommendations" in tool_names


def test_recommendation_skill_has_single_tool():
    plan = build_skill_plan(
        CopilotIntent.RECOMMENDATION,
    )

    assert plan is not None
    assert plan.skill_name == "Recommendation Review"
    assert len(plan.tools) == 1
    assert (
        plan.tools[0].capability_name
        == "get_operational_recommendations"
    )


def test_unknown_intent_has_no_skill():
    plan = build_skill_plan(
        CopilotIntent.UNKNOWN,
    )

    assert plan is None
