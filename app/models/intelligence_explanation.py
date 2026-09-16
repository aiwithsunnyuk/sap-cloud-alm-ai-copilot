from pydantic import BaseModel, Field


class OperationalExplanation(BaseModel):
    explanation_id: str
    severity: str
    title: str
    what_happened: str
    why_it_matters: str
    operational_impact: str
    evidence: list[str] = Field(default_factory=list)
    recommended_review: str


class ExplanationResponse(BaseModel):
    overall_status: str
    total_explanations: int
    critical_explanations: int
    high_explanations: int
    explanations: list[OperationalExplanation] = Field(default_factory=list)
