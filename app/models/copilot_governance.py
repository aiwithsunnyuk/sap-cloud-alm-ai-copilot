from enum import Enum

from pydantic import BaseModel


class CopilotActionClass(str, Enum):
    READ_ONLY = "read_only"
    ACTION = "action"
    HIGH_RISK_ACTION = "high_risk_action"


class CopilotGovernanceDecision(BaseModel):
    action_class: CopilotActionClass
    allowed: bool
    approval_required: bool
    reason: str
