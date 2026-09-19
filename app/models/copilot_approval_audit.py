from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.models.copilot_approval import CopilotApprovalStatus


class CopilotApprovalAuditRecord(BaseModel):
    audit_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)

    status: CopilotApprovalStatus

    approval_required: bool
    allowed_to_proceed: bool

    approver: str | None = None
    approval_comment: str | None = None

    rationale: str

    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    trace: list[str] = Field(default_factory=list)


class CopilotApprovalAuditSummary(BaseModel):
    total_records: int = Field(ge=0)
    pending: int = Field(ge=0)
    approved: int = Field(ge=0)
    rejected: int = Field(ge=0)
