from typing import Optional

from pydantic import BaseModel

from app.models.copilot import CopilotIntent
from app.models.copilot_skill_plan import CopilotSkillPlan


class CopilotAgentSkillPlan(BaseModel):
    agent_id: str
    agent_name: str
    intent: CopilotIntent
    skill: CopilotSkillPlan
    rationale: str
    trace: list[str] = []
