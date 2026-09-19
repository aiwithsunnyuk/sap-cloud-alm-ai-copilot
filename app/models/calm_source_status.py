from pydantic import BaseModel

from app.models.calm_connection import CalmConnectionStatus
from app.models.calm_data_source import CalmDataSource


class CalmSourceStatus(BaseModel):
    data_source: CalmDataSource
    configured: bool
    authenticated: bool
    connection_status: CalmConnectionStatus
    api_base_url: str
    message: str
