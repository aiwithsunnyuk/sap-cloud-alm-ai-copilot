from app.models.copilot import CopilotIntent
from app.services.copilot_orchestrator import orchestrate_skill


def test_deployment_skill_orchestrates_multiple_tools():
    result = orchestrate_skill(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    assert result is not None
    assert result.skill_name == "Deployment Investigation"
    assert result.intent == CopilotIntent.DEPLOYMENT
    assert result.status == "success"

    assert result.successful_tools == 3
    assert result.blocked_tools == 0
    assert result.failed_tools == 0
    assert result.approval_required is False

    tool_names = {
        item.tool_name
        for item in result.tool_results
    }

    assert tool_names == {
        "get_deployment_summary",
        "get_operational_correlations",
        "get_operational_recommendations",
    }

    for item in result.tool_results:
        assert item.status == "success"
        assert "Result Normalizer" in item.trace

    assert "Multi-Tool Orchestrator" in result.trace


def test_recommendation_skill_orchestrates_single_tool():
    result = orchestrate_skill(
        CopilotIntent.RECOMMENDATION
    )

    assert result is not None
    assert result.status == "success"
    assert result.successful_tools == 1
    assert len(result.tool_results) == 1

    assert (
        result.tool_results[0].tool_name
        == "get_operational_recommendations"
    )


def test_unknown_intent_has_no_orchestration_plan():
    result = orchestrate_skill(
        CopilotIntent.UNKNOWN
    )

    assert result is None
