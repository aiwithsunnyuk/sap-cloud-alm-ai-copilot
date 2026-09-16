from enum import Enum

from pydantic import BaseModel, Field


class CopilotIntent(str, Enum):
    PROJECT_HEALTH = "project_health"
    MONITORING = "monitoring"
    INCIDENT = "incident"
    PROBLEM = "problem"
    CHANGE = "change"
    RELEASE = "release"
    DEPLOYMENT = "deployment"
    CORRELATION = "correlation"
    EXPLANATION = "explanation"
    RECOMMENDATION = "recommendation"
    DECISION_BRIEF = "decision_brief"
    UNKNOWN = "unknown"


class CopilotQueryRequest(BaseModel):
    question: str = Field(min_length=3)


class CopilotRouteResponse(BaseModel):
    question: str
    intent: CopilotIntent
    confidence: float
    target_capability: str
    explanation: str
    suggested_endpoint: str | None = None
    evidence_required: bool = True
