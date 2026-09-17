from typing import List

from pydantic import BaseModel, Field

from app.models.copilot import CopilotIntent


class CopilotCapability(BaseModel):
    intent: CopilotIntent
    name: str
    description: str
    endpoint: str
    read_only: bool = True
    approval_required: bool = False
    supported_entity_types: List[str] = Field(default_factory=list)
