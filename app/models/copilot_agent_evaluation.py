from enum import Enum

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotAgentEvaluationStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class CopilotAgentEvaluationRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    intent: CopilotIntent

    requested_action: bool = False
    approved: bool = False

    skill_plan_valid: bool = True
    handoff_valid: bool = True
    execution_successful: bool = True
    grounded: bool = True

    trace: list[str] = Field(default_factory=list)


class CopilotAgentEvaluation(BaseModel):
    agent_id: str
    intent: CopilotIntent

    status: CopilotAgentEvaluationStatus
    score: int = Field(ge=0, le=100)

    governance_compliant: bool
    skill_plan_valid: bool
    handoff_valid: bool
    execution_successful: bool
    grounded: bool
    trace_complete: bool

    findings: list[str] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
