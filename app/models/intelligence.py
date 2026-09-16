from pydantic import BaseModel, Field


class OperationalInsight(BaseModel):
    insight_id: str
    severity: str
    category: str
    title: str
    summary: str
    evidence: list[str] = Field(default_factory=list)
    recommended_action: str


class IntelligenceResponse(BaseModel):
    overall_status: str
    total_insights: int
    critical_insights: int
    high_insights: int
    insights: list[OperationalInsight] = Field(default_factory=list)
