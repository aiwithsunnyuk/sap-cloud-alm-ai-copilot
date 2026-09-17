from typing import List

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent
from app.models.copilot_skill import CopilotSkillInvocation


class CopilotSkillPlan(BaseModel):
    skill_name: str
    description: str
    intent: CopilotIntent
    tools: List[CopilotSkillInvocation] = Field(default_factory=list)
    primary_tool: str
    read_only: bool = True
    approval_required: bool = False
