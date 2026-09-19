from enum import Enum

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotDecisionStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    BLOCKED = "blocked"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class CopilotAgentContribution(BaseModel):
    agent_id: str = Field(min_length=1)
    summary: str = Field(min_length=1)

    status: str = "success"

    findings: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class CopilotDecisionRequest(BaseModel):
    question: str = Field(min_length=3)
    intent: CopilotIntent

    contributions: list[CopilotAgentContribution] = Field(
        default_factory=list
    )


class CopilotDecisionResult(BaseModel):
    question: str
    intent: CopilotIntent

    status: CopilotDecisionStatus

    decision: str
    rationale: str

    contributing_agents: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    action_required: bool = False
    approval_required: bool = False

    trace: list[str] = Field(default_factory=list)
