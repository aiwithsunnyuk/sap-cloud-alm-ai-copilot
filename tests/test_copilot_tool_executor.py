from app.services.copilot_tool_executor import execute_tool


def test_deployment_tool_executes_through_trusted_dispatch():
    result = execute_tool(
        "get_deployment_summary"
    )

    assert result.status == "success"
    assert result.tool_name == "get_deployment_summary"
    assert result.source == "/deployments/summary"
    assert "Trusted Tool Executor" in result.trace
    assert "Trusted Service" in result.trace
    assert result.result is not None


def test_recommendation_tool_executes():
    result = execute_tool(
        "get_operational_recommendations"
    )

    assert result.status == "success"
    assert result.tool_name == (
        "get_operational_recommendations"
    )
    assert result.result is not None


def test_unknown_tool_is_blocked():
    result = execute_tool(
        "not_a_real_tool"
    )

    assert result.status == "blocked"
    assert result.result is None
    assert "Tool Not Found" in result.trace


def test_unapproved_action_is_blocked():
    from app.models.copilot_tool import CopilotTool
    from app.models.copilot import CopilotIntent
    from app.services import copilot_tool_executor
    from app.services import copilot_tool_registry

    original = copilot_tool_executor.get_tool

    fake_tool = CopilotTool(
        tool_name="test_action",
        description="Test governed action",
        intent=CopilotIntent.DEPLOYMENT,
        endpoint="/test-action",
        service_function="not.executed",
        read_only=False,
        approval_required=True,
    )

    copilot_tool_executor.get_tool = (
        lambda tool_name: fake_tool
        if tool_name == "test_action"
        else original(tool_name)
    )

    try:
        result = copilot_tool_executor.execute_tool(
            "test_action"
        )

        assert result.status == "approval_required"
        assert result.approval_required is True
        assert "Approval Required" in result.trace
    finally:
        copilot_tool_executor.get_tool = original
