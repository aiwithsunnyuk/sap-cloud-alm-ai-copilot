from pydantic import BaseModel, Field


class DecisionBriefResponse(BaseModel):
    brief_id: str
    overall_status: str
    executive_summary: str
    total_risks: int
    priority_actions_count: int
    top_risks: list[str] = Field(default_factory=list)
    priority_actions: list[str] = Field(default_factory=list)
    affected_components: list[str] = Field(default_factory=list)
    affected_workstreams: list[str] = Field(default_factory=list)
    decision_points: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
