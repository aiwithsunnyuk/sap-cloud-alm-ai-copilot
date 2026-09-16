from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotResponse(BaseModel):
    question: str
    intent: CopilotIntent
    confidence: float
    answer: str
    evidence: list[str] = Field(default_factory=list)
    source_capability: str
    source_endpoint: str | None = None
    trace: list[str] = Field(default_factory=list)
    grounded: bool = True
    action_required: bool = False
    approval_required: bool = False
