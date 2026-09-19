from pydantic import BaseModel

from app.models.copilot_decision_assessment import CopilotDecisionAssessment


class CopilotDecisionApprovalRequest(BaseModel):
    assessment: CopilotDecisionAssessment

    approver: str | None = None
    approval_comment: str | None = None
