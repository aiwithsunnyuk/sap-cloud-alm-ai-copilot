from typing import Dict, List, Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_capability import CopilotCapability


_CAPABILITIES: Dict[CopilotIntent, CopilotCapability] = {
    CopilotIntent.PROJECT_HEALTH: CopilotCapability(
        intent=CopilotIntent.PROJECT_HEALTH,
        name="Operations Control Tower",
        description="Overall delivery and operational health.",
        endpoint="/operations/control-tower",
        supported_entity_types=["project", "workstream"],
    ),
    CopilotIntent.MONITORING: CopilotCapability(
        intent=CopilotIntent.MONITORING,
        name="Monitoring Intelligence",
        description="Monitoring events, alerts, and operational health.",
        endpoint="/monitoring/health",
        supported_entity_types=["alert", "monitoring_event"],
    ),
    CopilotIntent.INCIDENT: CopilotCapability(
        intent=CopilotIntent.INCIDENT,
        name="Incident Intelligence",
        description="Incident status, severity, priority, and details.",
        endpoint="/incidents",
        supported_entity_types=["incident"],
    ),
    CopilotIntent.PROBLEM: CopilotCapability(
        intent=CopilotIntent.PROBLEM,
        name="Problem Intelligence",
        description="Problem investigation and root-cause information.",
        endpoint="/problems",
        supported_entity_types=["problem", "incident"],
    ),
    CopilotIntent.CHANGE: CopilotCapability(
        intent=CopilotIntent.CHANGE,
        name="Change Intelligence",
        description="Change assessment, approval, and implementation state.",
        endpoint="/changes",
        supported_entity_types=["change", "problem", "incident"],
    ),
    CopilotIntent.RELEASE: CopilotCapability(
        intent=CopilotIntent.RELEASE,
        name="Release Intelligence",
        description="Release readiness and governance information.",
        endpoint="/releases",
        supported_entity_types=["release", "change"],
    ),
    CopilotIntent.DEPLOYMENT: CopilotCapability(
        intent=CopilotIntent.DEPLOYMENT,
        name="Deployment Intelligence",
        description="Deployment status, validation, and rollback information.",
        endpoint="/deployments/summary",
        supported_entity_types=["deployment", "release", "change"],
    ),
    CopilotIntent.CORRELATION: CopilotCapability(
        intent=CopilotIntent.CORRELATION,
        name="Operational Correlation",
        description="Cross-domain relationships between operational objects.",
        endpoint="/intelligence/correlations",
        supported_entity_types=[
            "monitoring_event",
            "incident",
            "problem",
            "change",
            "release",
            "deployment",
        ],
    ),
    CopilotIntent.EXPLANATION: CopilotCapability(
        intent=CopilotIntent.EXPLANATION,
        name="Operational Explanation",
        description="Explain operational impact and supporting evidence.",
        endpoint="/intelligence/explanations",
        supported_entity_types=[
            "incident",
            "problem",
            "change",
            "release",
            "deployment",
        ],
    ),
    CopilotIntent.RECOMMENDATION: CopilotCapability(
        intent=CopilotIntent.RECOMMENDATION,
        name="Operational Recommendations",
        description="Prioritized operational actions and review recommendations.",
        endpoint="/intelligence/recommendations",
        supported_entity_types=[
            "incident",
            "problem",
            "change",
            "release",
            "deployment",
        ],
    ),
    CopilotIntent.DECISION_BRIEF: CopilotCapability(
        intent=CopilotIntent.DECISION_BRIEF,
        name="Executive Decision Brief",
        description="Consolidated operational risks and priority actions.",
        endpoint="/intelligence/decision-brief",
        supported_entity_types=["project", "workstream", "incident", "release"],
    ),
}


def get_capability(
    intent: CopilotIntent,
) -> Optional[CopilotCapability]:
    return _CAPABILITIES.get(intent)


def get_all_capabilities() -> List[CopilotCapability]:
    return list(_CAPABILITIES.values())


def get_capability_by_name(
    name: str,
) -> Optional[CopilotCapability]:
    normalized = name.strip().lower()

    for capability in _CAPABILITIES.values():
        if capability.name.lower() == normalized:
            return capability

    return None
