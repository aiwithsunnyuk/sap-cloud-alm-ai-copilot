from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotAgentHandoff(BaseModel):
    source_agent_id: str
    target_agent_id: Optional[str] = None
    target_agent_name: Optional[str] = None
    target_intent: CopilotIntent
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    status: str
    reason: str
    approval_required: bool = False
    trace: List[str] = Field(default_factory=list)
