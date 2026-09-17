from app.models.copilot import CopilotIntent
from app.services.copilot_tool_registry import (
    get_all_tools,
    get_tool,
    get_tools_for_intent,
)


def test_tool_registry_contains_expected_tools():
    tools = get_all_tools()

    names = {tool.tool_name for tool in tools}

    expected = {
        "get_project_health",
        "get_monitoring_health",
        "get_incident_summary",
        "get_problem_summary",
        "get_change_summary",
        "get_release_summary",
        "get_deployment_summary",
        "get_operational_correlations",
        "get_operational_explanations",
        "get_operational_recommendations",
        "get_decision_brief",
    }

    assert names == expected
    assert len(tools) == 11


def test_deployment_tool_contract():
    tool = get_tool("get_deployment_summary")

    assert tool is not None
    assert tool.intent == CopilotIntent.DEPLOYMENT
    assert tool.endpoint == "/deployments/summary"
    assert tool.read_only is True
    assert tool.approval_required is False
    assert "deployment" in tool.supported_entity_types
    assert tool.service_function


def test_tools_can_be_discovered_by_intent():
    tools = get_tools_for_intent(
        CopilotIntent.RECOMMENDATION
    )

    assert len(tools) == 1
    assert tools[0].tool_name == "get_operational_recommendations"
    assert (
        tools[0].endpoint
        == "/intelligence/recommendations"
    )


def test_unknown_tool_returns_none():
    assert get_tool("not_a_real_tool") is None
