from typing import List

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotAgent(BaseModel):
    agent_id: str
    name: str
    description: str
    intents: List[CopilotIntent] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    read_only: bool = True
    approval_required: bool = False
