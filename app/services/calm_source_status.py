import os

from app.models.calm_connection import CalmConnectionStatus
from app.models.calm_data_source import CalmDataSource
from app.models.calm_source_status import CalmSourceStatus
from app.services.sap_cloud_alm_client import SapCloudAlmClient


def _get_data_source() -> CalmDataSource:
    raw = os.getenv(
        "SAP_CALM_DATA_SOURCE",
        CalmDataSource.SYNTHETIC.value,
    ).strip().lower()

    try:
        return CalmDataSource(raw)
    except ValueError:
        return CalmDataSource.SYNTHETIC


def get_calm_source_status() -> CalmSourceStatus:
    source = _get_data_source()

    if source == CalmDataSource.SYNTHETIC:
        return CalmSourceStatus(
            data_source=CalmDataSource.SYNTHETIC,
            configured=True,
            authenticated=False,
            connection_status=CalmConnectionStatus.NOT_CONFIGURED,
            api_base_url="",
            message=(
                "Synthetic task data source is active. "
                "SAP Cloud ALM is not required."
            ),
        )

    client = SapCloudAlmClient.from_environment()

    if client is None:
        return CalmSourceStatus(
            data_source=CalmDataSource.SAP,
            configured=False,
            authenticated=False,
            connection_status=CalmConnectionStatus.NOT_CONFIGURED,
            api_base_url="",
            message=(
                "SAP Cloud ALM is selected but credentials "
                "are not configured."
            ),
        )

    connection = client.connection_status()

    return CalmSourceStatus(
        data_source=CalmDataSource.SAP,
        configured=True,
        authenticated=connection.authenticated,
        connection_status=connection.status,
        api_base_url=connection.api_base_url,
        message=connection.message,
    )
