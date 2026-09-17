from typing import List

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent
from app.models.copilot_normalized_result import CopilotNormalizedResult


class CopilotOrchestrationResult(BaseModel):
    skill_name: str
    intent: CopilotIntent
    status: str
    tool_results: List[CopilotNormalizedResult] = Field(
        default_factory=list
    )
    successful_tools: int = 0
    blocked_tools: int = 0
    failed_tools: int = 0
    approval_required: bool = False
    trace: List[str] = Field(default_factory=list)
