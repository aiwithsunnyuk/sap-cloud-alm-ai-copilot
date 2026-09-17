from typing import Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_orchestration import CopilotOrchestrationResult
from app.services.copilot_result_normalizer import (
    normalize_tool_result,
)
from app.services.copilot_skill_planner import build_skill_plan
from app.services.copilot_tool_executor import execute_tool


def orchestrate_skill(
    intent: CopilotIntent,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> Optional[CopilotOrchestrationResult]:
    plan = build_skill_plan(
        intent,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    if plan is None:
        return None

    normalized_results = []

    successful = 0
    blocked = 0
    failed = 0
    approval_required = False

    trace = [
        "Skill Planner",
        "Multi-Tool Orchestrator",
    ]

    for tool in plan.tools:
        tool_result = execute_tool(
            tool.capability_name
        )

        normalized = normalize_tool_result(
            tool_result
        )

        normalized_results.append(normalized)

        if normalized.status == "success":
            successful += 1
        elif normalized.status in {
            "blocked",
            "approval_required",
        }:
            blocked += 1
        else:
            failed += 1

        if normalized.approval_required:
            approval_required = True

    if failed > 0:
        status = "partial_failure"
    elif blocked > 0:
        status = "partially_blocked"
    else:
        status = "success"

    trace.append("Normalized Tool Results")

    if approval_required:
        trace.append("Approval Gate")

    return CopilotOrchestrationResult(
        skill_name=plan.skill_name,
        intent=plan.intent,
        status=status,
        tool_results=normalized_results,
        successful_tools=successful,
        blocked_tools=blocked,
        failed_tools=failed,
        approval_required=approval_required,
        trace=trace,
    )
