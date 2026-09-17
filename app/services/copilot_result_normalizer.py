from typing import Any, Dict

from app.models.copilot_normalized_result import (
    CopilotNormalizedResult,
)
from app.models.copilot_tool_result import CopilotToolResult


def normalize_tool_result(
    result: CopilotToolResult,
) -> CopilotNormalizedResult:
    data = _to_data(result.result)

    summary = _build_summary(
        tool_name=result.tool_name,
        status=result.status,
        data=data,
    )

    evidence = list(result.evidence)

    if not evidence:
        evidence = _derive_evidence(data)

    trace = list(result.trace)

    if "Result Normalizer" not in trace:
        trace.append("Result Normalizer")

    return CopilotNormalizedResult(
        tool_name=result.tool_name,
        status=result.status,
        summary=summary,
        data=data,
        evidence=evidence,
        source=result.source,
        trace=trace,
        approval_required=result.approval_required,
    )


def _to_data(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}

    if hasattr(value, "model_dump"):
        dumped = value.model_dump()

        if isinstance(dumped, dict):
            return dumped

    if isinstance(value, dict):
        return dict(value)

    if isinstance(value, list):
        return {
            "items": value,
            "item_count": len(value),
        }

    return {
        "value": value,
    }


def _build_summary(
    *,
    tool_name: str,
    status: str,
    data: Dict[str, Any],
) -> str:
    if status != "success":
        return (
            f"Tool '{tool_name}' completed with status "
            f"'{status}'."
        )

    if tool_name == "get_deployment_summary":
        total = data.get("total_deployments", 0)
        rolled_back = data.get("rolled_back_deployments", 0)
        failed_validation = data.get("failed_validations", 0)

        return (
            f"Deployment summary contains {total} deployment(s), "
            f"{rolled_back} rolled-back deployment(s), and "
            f"{failed_validation} failed validation(s)."
        )

    if tool_name == "get_operational_recommendations":
        total = data.get("total_recommendations", 0)
        p1 = data.get("p1_recommendations", 0)
        p2 = data.get("p2_recommendations", 0)

        return (
            f"Operational recommendations include {total} "
            f"recommendation(s), including {p1} P1 and {p2} P2."
        )

    if tool_name == "get_incident_summary":
        total = data.get("total_incidents", 0)
        open_count = data.get("open_incidents", 0)

        return (
            f"Incident summary contains {total} incident(s), "
            f"including {open_count} open incident(s)."
        )

    return (
        f"Tool '{tool_name}' completed successfully "
        f"with {len(data)} normalized field(s)."
    )


def _derive_evidence(
    data: Dict[str, Any],
) -> list[str]:
    evidence = []

    evidence_keys = (
        "total_deployments",
        "rolled_back_deployments",
        "failed_validations",
        "total_recommendations",
        "p1_recommendations",
        "p2_recommendations",
        "total_incidents",
        "open_incidents",
    )

    for key in evidence_keys:
        if key in data:
            label = key.replace("_", " ").title()
            evidence.append(
                f"{label}: {data[key]}"
            )

    return evidence
