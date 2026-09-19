from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent
from app.models.copilot_orchestration import CopilotOrchestrationResult


class CopilotAgentOrchestrationInput(BaseModel):
    agent_id: str = Field(min_length=1)
    orchestration: CopilotOrchestrationResult


class CopilotMultiAgentDecisionRequest(BaseModel):
    question: str = Field(min_length=3)
    intent: CopilotIntent

    agent_results: list[CopilotAgentOrchestrationInput] = Field(
        default_factory=list
    )
