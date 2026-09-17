from typing import Any, List

from pydantic import BaseModel, Field


class CopilotToolResult(BaseModel):
    tool_name: str
    status: str
    result: Any = None
    evidence: List[str] = Field(default_factory=list)
    source: str
    trace: List[str] = Field(default_factory=list)
    approval_required: bool = False
