from pydantic import BaseModel, Field

from app.models.copilot_approval import CopilotApprovalResult
from app.models.copilot_approval_audit import CopilotApprovalAuditRecord
from app.models.copilot_decision_assessment import CopilotDecisionAssessment


class CopilotDecisionApprovalResult(BaseModel):
    decision_id: str

    assessment: CopilotDecisionAssessment
    approval: CopilotApprovalResult

    audit_record: CopilotApprovalAuditRecord

    allowed_to_proceed: bool

    trace: list[str] = Field(default_factory=list)
