from typing import List

from pydantic import BaseModel, Field


class CopilotAgentGovernance(BaseModel):
    agent_id: str
    agent_name: str
    allowed: bool
    read_only: bool
    approval_required: bool
    reason: str
    trace: List[str] = Field(default_factory=list)
