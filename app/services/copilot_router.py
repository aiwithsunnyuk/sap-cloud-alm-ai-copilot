import re

from app.models.copilot import (
    CopilotIntent,
    CopilotQueryRequest,
    CopilotRouteResponse,
)


_INTENT_RULES = [
    (
        CopilotIntent.DECISION_BRIEF,
        (
            "decision brief",
            "executive brief",
            "executive summary",
            "management summary",
        ),
        "Decision Brief",
        "/intelligence/decision-brief",
    ),
    (
        CopilotIntent.DEPLOYMENT,
        (
            "deployment",
            "rolled back",
            "rollback",
            "validation failed",
            "failed validation",
            "deployment status",
            "deployment validation",
        ),
        "Deployment Intelligence",
        "/deployments/summary",
    ),
    (
        CopilotIntent.RELEASE,
        (
            "release governance",
            "release eligible",
            "ready for release",
            "release",
        ),
        "Release Governance",
        "/releases/summary",
    ),
    (
        CopilotIntent.CHANGE,
        (
            "change approval",
            "change request",
            "pending approval",
            "change",
        ),
        "Change Management",
        "/changes/summary",
    ),
    (
        CopilotIntent.PROBLEM,
        (
            "root cause",
            "rca",
            "problem",
            "unresolved root cause",
        ),
        "Problem Management",
        "/problems/summary",
    ),
    (
        CopilotIntent.INCIDENT,
        (
            "critical incident",
            "open incident",
            "incident",
        ),
        "Incident Management",
        "/incidents/summary",
    ),
    (
        CopilotIntent.MONITORING,
        (
            "active alerts",
            "operational health",
            "monitoring",
            "monitor",
            "alert",
        ),
        "Monitoring Intelligence",
        "/monitoring/health",
    ),
    (
        CopilotIntent.CORRELATION,
        (
            "causal chain",
            "operational chain",
            "related objects",
            "what is connected",
            "trace the issue",
            "correlation",
        ),
        "Operational Correlations",
        "/intelligence/correlations",
    ),
    (
        CopilotIntent.RECOMMENDATION,
        (
            "what should i do",
            "what should we do",
            "what needs attention",
            "next action",
            "recommendation",
            "recommendations",
            "priority",
            "prioritize",
        ),
        "Operational Recommendations",
        "/intelligence/recommendations",
    ),
    (
        CopilotIntent.EXPLANATION,
        (
            "why is",
            "why was",
            "why did",
            "explain",
            "what caused",
            "why critical",
        ),
        "Operational Explainability",
        "/intelligence/explanations",
    ),
    (
        CopilotIntent.PROJECT_HEALTH,
        (
            "project health",
            "overall health",
            "current status",
            "project status",
            "why is the project",
            "is the project healthy",
            "how is the project",
        ),
        "Operations Control Tower",
        "/operations/control-tower",
    ),
]



def _normalize(question: str) -> str:
    question = question.lower().strip()
    return re.sub(r"\s+", " ", question)


def classify_copilot_query(
    request: CopilotQueryRequest,
) -> CopilotRouteResponse:
    question = _normalize(request.question)

    for intent, phrases, capability, endpoint in _INTENT_RULES:
        for phrase in phrases:
            if phrase in question:
                return CopilotRouteResponse(
                    question=request.question,
                    intent=intent,
                    confidence=0.90,
                    target_capability=capability,
                    explanation=(
                        f"Matched the query to the {capability} "
                        "capability using deterministic intent rules."
                    ),
                    suggested_endpoint=endpoint,
                )

    return CopilotRouteResponse(
        question=request.question,
        intent=CopilotIntent.UNKNOWN,
        confidence=0.0,
        target_capability="No trusted capability identified",
        explanation=(
            "The current deterministic router could not map the "
            "question to a trusted operational capability."
        ),
        suggested_endpoint=None,
        evidence_required=True,
    )
