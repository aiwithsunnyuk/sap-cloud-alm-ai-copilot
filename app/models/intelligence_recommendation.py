from pydantic import BaseModel, Field


class OperationalRecommendation(BaseModel):
    recommendation_id: str
    priority: str
    priority_score: int
    severity: str
    title: str
    action: str
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    source_explanation: str


class RecommendationResponse(BaseModel):
    overall_status: str
    total_recommendations: int
    p1_recommendations: int
    p2_recommendations: int
    recommendations: list[OperationalRecommendation] = Field(
        default_factory=list
    )
