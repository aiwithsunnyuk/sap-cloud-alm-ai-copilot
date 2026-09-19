from pydantic import BaseModel

from app.models.copilot_decision import CopilotDecisionResult
from app.models.copilot_decision_confidence import CopilotDecisionConfidence


class CopilotDecisionOrchestrationResponse(BaseModel):
    decision: CopilotDecisionResult
    confidence: CopilotDecisionConfidence
