from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotAgentSelection(BaseModel):
    intent: CopilotIntent
    status: str
    selected_agent_id: Optional[str] = None
    selected_agent_name: Optional[str] = None
    candidate_agent_ids: List[str] = Field(
        default_factory=list
    )
    entity_type: Optional[str] = None
    rationale: str
    trace: List[str] = Field(default_factory=list)
