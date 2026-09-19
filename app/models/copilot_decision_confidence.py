from enum import Enum

from pydantic import BaseModel, Field

from app.models.copilot_decision import CopilotDecisionStatus


class CopilotDecisionConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class CopilotDecisionConfidence(BaseModel):
    score: int = Field(ge=0, le=100)
    level: CopilotDecisionConfidenceLevel

    decision_status: CopilotDecisionStatus

    contributing_agents: int = Field(ge=0)
    evidence_items: int = Field(ge=0)
    recommendations: int = Field(ge=0)

    rationale: str
