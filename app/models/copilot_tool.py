from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotTool(BaseModel):
    tool_name: str
    description: str
    intent: CopilotIntent
    endpoint: str
    service_function: str
    read_only: bool = True
    approval_required: bool = False
    supported_entity_types: List[str] = Field(default_factory=list)
    input_description: Optional[str] = None
