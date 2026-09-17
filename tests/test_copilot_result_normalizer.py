from app.models.copilot_tool_result import CopilotToolResult
from app.services.copilot_result_normalizer import (
    normalize_tool_result,
)


def test_deployment_result_is_normalized():
    result = CopilotToolResult(
        tool_name="get_deployment_summary",
        status="success",
        result={
            "total_deployments": 3,
            "successful_deployments": 2,
            "rolled_back_deployments": 1,
            "failed_validations": 1,
        },
        evidence=[],
        source="/deployments/summary",
        trace=["Trusted Tool Executor"],
    )

    normalized = normalize_tool_result(result)

    assert normalized.tool_name == (
        "get_deployment_summary"
    )
    assert normalized.status == "success"
    assert normalized.data["total_deployments"] == 3
    assert normalized.data["rolled_back_deployments"] == 1
    assert normalized.summary.startswith(
        "Deployment summary contains"
    )
    assert "Rolled Back Deployments: 1" in (
        normalized.evidence
    )[1]
    assert "Result Normalizer" in normalized.trace


def test_primitive_result_is_wrapped():
    result = CopilotToolResult(
        tool_name="test_tool",
        status="success",
        result="hello",
        source="/test",
        trace=[],
    )

    normalized = normalize_tool_result(result)

    assert normalized.data["value"] == "hello"
    assert normalized.status == "success"
    assert normalized.summary.startswith(
        "Tool 'test_tool' completed successfully"
    )
    assert "Result Normalizer" in normalized.trace


def test_list_result_is_normalized():
    result = CopilotToolResult(
        tool_name="test_tool",
        status="success",
        result=["A", "B", "C"],
        source="/test",
        trace=[],
    )

    normalized = normalize_tool_result(result)

    assert normalized.data["items"] == [
        "A",
        "B",
        "C",
    ]
    assert normalized.data["item_count"] == 3


def test_failed_result_preserves_governance_state():
    result = CopilotToolResult(
        tool_name="test_action",
        status="approval_required",
        result=None,
        source="/test-action",
        trace=["Governance Check"],
        approval_required=True,
    )

    normalized = normalize_tool_result(result)

    assert normalized.status == "approval_required"
    assert normalized.approval_required is True
    assert normalized.data == {}
    assert "Result Normalizer" in normalized.trace
