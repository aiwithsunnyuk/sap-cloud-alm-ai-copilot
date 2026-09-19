from app.models.copilot import CopilotIntent
from app.models.copilot_normalized_result import CopilotNormalizedResult
from app.models.copilot_orchestration import CopilotOrchestrationResult
from app.services.copilot_agent_contribution_adapter import (
    build_agent_contribution,
)


def _orchestration(
    *,
    tool_results=None,
    status="success",
    successful_tools=1,
    blocked_tools=0,
    failed_tools=0,
):
    return CopilotOrchestrationResult(
        skill_name="Deployment Investigation",
        intent=CopilotIntent.DEPLOYMENT,
        status=status,
        tool_results=tool_results or [],
        successful_tools=successful_tools,
        blocked_tools=blocked_tools,
        failed_tools=failed_tools,
        approval_required=False,
        trace=[
            "Skill Planning",
            "Tool Execution",
            "Normalized Tool Results",
        ],
    )


def test_successful_orchestration_becomes_agent_contribution():
    result = build_agent_contribution(
        "deployment-investigator",
        _orchestration(
            tool_results=[
                CopilotNormalizedResult(
                    tool_name="get_deployment_summary",
                    status="success",
                    summary="DEP-001 was rolled back.",
                    data={
                        "findings": [
                            "DEP-001 validation failed."
                        ],
                        "recommendations": [
                            "Review rollback corrective actions."
                        ],
                    },
                    evidence=[
                        "DEP-001: rollback completed"
                    ],
                    source="deployment service",
                    trace=["Tool Execution"],
                    approval_required=False,
                )
            ]
        ),
    )

    assert result.agent_id == "deployment-investigator"
    assert result.status == "success"

    assert result.findings == [
        "DEP-001 validation failed."
    ]
    assert result.evidence == [
        "DEP-001: rollback completed"
    ]
    assert result.recommendations == [
        "Review rollback corrective actions."
    ]

    assert "Deployment Investigator" in result.summary


def test_multiple_tool_results_are_aggregated_and_deduplicated():
    result = build_agent_contribution(
        "deployment-investigator",
        _orchestration(
            tool_results=[
                CopilotNormalizedResult(
                    tool_name="get_deployment_summary",
                    status="success",
                    summary="Deployment summary",
                    data={
                        "findings": ["Deployment failed"],
                        "recommendations": ["Review validation"],
                    },
                    evidence=["DEP-001"],
                    source="deployment service",
                    trace=[],
                    approval_required=False,
                ),
                CopilotNormalizedResult(
                    tool_name="get_operational_correlations",
                    status="success",
                    summary="Correlation found",
                    data={
                        "findings": ["Deployment failed"],
                        "recommendations": ["Review validation"],
                    },
                    evidence=["DEP-001", "INC-003"],
                    source="correlation service",
                    trace=[],
                    approval_required=False,
                ),
            ]
        ),
    )

    assert result.status == "success"
    assert result.evidence == ["DEP-001", "INC-003"]
    assert result.findings == ["Deployment failed"]
    assert result.recommendations == ["Review validation"]


def test_failed_tool_execution_becomes_failed_agent_contribution():
    result = build_agent_contribution(
        "deployment-investigator",
        _orchestration(
            status="partial_failure",
            successful_tools=2,
            failed_tools=1,
        ),
    )

    assert result.status == "failed"
    assert "1 tool(s) failed" in result.summary


def test_blocked_tool_execution_becomes_blocked_agent_contribution():
    result = build_agent_contribution(
        "deployment-investigator",
        _orchestration(
            status="partially_blocked",
            successful_tools=2,
            blocked_tools=1,
        ),
    )

    assert result.status == "blocked"
    assert "1 tool(s) were blocked" in result.summary


def test_unknown_agent_is_represented_without_inventing_evidence():
    result = build_agent_contribution(
        "unknown-agent",
        _orchestration(
            tool_results=[
                CopilotNormalizedResult(
                    tool_name="get_deployment_summary",
                    status="success",
                    summary="Some result",
                    data={"findings": ["should not be trusted here"]},
                    evidence=["DEP-001"],
                    source="deployment service",
                    trace=[],
                    approval_required=False,
                )
            ]
        ),
    )

    assert result.agent_id == "unknown-agent"
    assert result.status == "failed"
    assert result.findings == []
    assert result.evidence == []
    assert result.recommendations == []
    assert result.summary == "Unknown agent: unknown-agent"


def test_adapter_preserves_clean_success_without_evidence():
    result = build_agent_contribution(
        "incident-investigator",
        _orchestration(
            tool_results=[
                CopilotNormalizedResult(
                    tool_name="get_incident_summary",
                    status="success",
                    summary="Incident check completed.",
                    data={},
                    evidence=[],
                    source="incident service",
                    trace=[],
                    approval_required=False,
                )
            ]
        ),
    )

    assert result.status == "success"
    assert result.evidence == []
    assert result.findings == []
    assert result.recommendations == []
    assert "Incident Investigator" in result.summary
