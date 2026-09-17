from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CopilotEntityReference(BaseModel):
    entity_type: str
    entity_id: str
    display_name: str
    confidence: float = 1.0


class CopilotEntityContext(BaseModel):
    primary: Optional[CopilotEntityReference] = None
    related_entities: List[CopilotEntityReference] = Field(default_factory=list)
    relationship_path: List[str] = Field(default_factory=list)
    attributes: Dict[str, str] = Field(default_factory=dict)
