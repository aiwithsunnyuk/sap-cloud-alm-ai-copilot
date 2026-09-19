from pydantic import BaseModel, Field

from app.models.copilot_decision import CopilotDecisionResult
from app.models.copilot_decision_confidence import CopilotDecisionConfidence


class CopilotDecisionAssessment(BaseModel):
    decision: CopilotDecisionResult
    confidence: CopilotDecisionConfidence

    auditable: bool = True
    review_required: bool = False

    trace: list[str] = Field(default_factory=list)
