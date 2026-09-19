from enum import Enum

from pydantic import BaseModel, Field


class CalmConnectionStatus(str, Enum):
    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"
    AUTHENTICATED = "authenticated"
    AUTHENTICATION_FAILED = "authentication_failed"


class CalmConnectionConfig(BaseModel):
    api_base_url: str = Field(min_length=1)
    token_url: str = Field(min_length=1)
    client_id: str = Field(min_length=1)
    client_secret: str = Field(min_length=1)


class CalmConnectionResult(BaseModel):
    status: CalmConnectionStatus
    authenticated: bool
    api_base_url: str
    message: str
