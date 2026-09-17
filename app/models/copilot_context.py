from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class CopilotContextTurn(BaseModel):
    question: str
    intent: str
    answer: str
    source_capability: Optional[str] = None
    grounded: bool = False
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class CopilotConversationContext(BaseModel):
    conversation_id: str
    turns: List[CopilotContextTurn] = Field(default_factory=list)

    @property
    def latest_turn(self) -> Optional[CopilotContextTurn]:
        return self.turns[-1] if self.turns else None
