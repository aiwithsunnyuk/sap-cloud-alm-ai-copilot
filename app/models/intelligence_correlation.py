from pydantic import BaseModel, Field


class CorrelatedObject(BaseModel):
    object_type: str
    object_id: str


class OperationalCorrelation(BaseModel):
    correlation_id: str
    severity: str
    title: str
    summary: str
    related_objects: list[CorrelatedObject] = Field(default_factory=list)
    causal_chain: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    recommended_action: str


class CorrelationResponse(BaseModel):
    overall_status: str
    total_correlations: int
    critical_correlations: int
    high_correlations: int
    correlations: list[OperationalCorrelation] = Field(default_factory=list)
