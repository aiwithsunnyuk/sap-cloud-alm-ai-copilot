from typing import List, Optional

from pydantic import BaseModel, Field


class CopilotSessionSummary(BaseModel):
    conversation_id: str
    turn_count: int = 0
    latest_intent: Optional[str] = None
    current_entity_type: Optional[str] = None
    current_entity_id: Optional[str] = None
    related_entities: List[str] = Field(default_factory=list)
    evidence_count: int = 0
    grounded_turn_count: int = 0
