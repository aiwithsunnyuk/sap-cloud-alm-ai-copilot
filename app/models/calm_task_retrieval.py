from typing import Any

from pydantic import BaseModel, Field

from app.models.calm_data_source import CalmDataSource


class CalmTaskRetrievalResponse(BaseModel):
    data_source: CalmDataSource
    count: int = Field(ge=0)
    tasks: list[dict[str, Any]] = Field(default_factory=list)
