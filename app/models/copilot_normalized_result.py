from typing import Any, Dict, List

from pydantic import BaseModel, Field


class CopilotNormalizedResult(BaseModel):
    tool_name: str
    status: str
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    source: str
    trace: List[str] = Field(default_factory=list)
    approval_required: bool = False
