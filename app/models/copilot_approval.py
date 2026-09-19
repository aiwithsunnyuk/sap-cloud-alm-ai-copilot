from enum import Enum

from pydantic import BaseModel, Field

from app.models.copilot_decision import CopilotDecisionStatus
from app.models.copilot_decision_confidence import (
    CopilotDecisionConfidenceLevel,
)


class CopilotApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CopilotApprovalRequest(BaseModel):
    decision_id: str = Field(min_length=1)

    decision_status: CopilotDecisionStatus
    confidence_score: int = Field(ge=0, le=100)
    confidence_level: CopilotDecisionConfidenceLevel

    requested_action: bool = False

    approver: str | None = None
    approval_comment: str | None = None


class CopilotApprovalResult(BaseModel):
    decision_id: str

    status: CopilotApprovalStatus

    allowed_to_proceed: bool
    approval_required: bool

    approver: str | None = None
    approval_comment: str | None = None

    rationale: str

    trace: list[str] = Field(default_factory=list)
