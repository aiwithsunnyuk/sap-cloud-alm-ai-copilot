from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent
from app.models.copilot_governance import CopilotActionClass


class CopilotSkillInvocation(BaseModel):
    intent: CopilotIntent
    capability_name: str
    endpoint: str
    parameters: Dict[str, str] = Field(default_factory=dict)
    read_only: bool = True
    approval_required: bool = False
    action_class: CopilotActionClass = CopilotActionClass.READ_ONLY
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
