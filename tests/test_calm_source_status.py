from unittest.mock import patch

from app.models.calm_connection import CalmConnectionStatus
from app.models.calm_data_source import CalmDataSource
from app.services.calm_source_status import (
    get_calm_source_status,
)


def test_default_source_status_is_synthetic():
    with patch.dict(
        "os.environ",
        {},
        clear=True,
    ):
        result = get_calm_source_status()

    assert result.data_source == CalmDataSource.SYNTHETIC
    assert result.configured is True
    assert result.authenticated is False
    assert result.connection_status == (
        CalmConnectionStatus.NOT_CONFIGURED
    )


def test_synthetic_source_status_does_not_require_credentials():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "synthetic",
            "SAP_CALM_CLIENT_SECRET": "should-not-matter",
        },
        clear=True,
    ):
        result = get_calm_source_status()

    assert result.data_source == CalmDataSource.SYNTHETIC
    assert result.configured is True
    assert "Synthetic" in result.message


def test_sap_source_without_credentials_is_not_configured():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "sap",
        },
        clear=True,
    ):
        with patch(
            "app.services.calm_source_status.SapCloudAlmClient."
            "from_environment",
            return_value=None,
        ):
            result = get_calm_source_status()

    assert result.data_source == CalmDataSource.SAP
    assert result.configured is False
    assert result.authenticated is False
    assert result.connection_status == (
        CalmConnectionStatus.NOT_CONFIGURED
    )


def test_sap_source_reports_authenticated():
    fake_client = object()

    fake_connection = type(
        "Connection",
        (),
        {
            "authenticated": True,
            "status": CalmConnectionStatus.AUTHENTICATED,
            "api_base_url": (
                "https://tenant.example/api"
            ),
            "message": "SAP Cloud ALM OAuth authentication succeeded.",
        },
    )()

    fake_client = type(
        "Client",
        (),
        {
            "connection_status": lambda self: fake_connection,
        },
    )()

    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "sap",
        },
        clear=True,
    ):
        with patch(
            "app.services.calm_source_status.SapCloudAlmClient."
            "from_environment",
            return_value=fake_client,
        ):
            result = get_calm_source_status()

    assert result.data_source == CalmDataSource.SAP
    assert result.configured is True
    assert result.authenticated is True
    assert result.connection_status == (
        CalmConnectionStatus.AUTHENTICATED
    )
    assert result.api_base_url == "https://tenant.example/api"


def test_sap_source_reports_authentication_failure():
    fake_connection = type(
        "Connection",
        (),
        {
            "authenticated": False,
            "status": CalmConnectionStatus.AUTHENTICATION_FAILED,
            "api_base_url": (
                "https://tenant.example/api"
            ),
            "message": "SAP Cloud ALM authentication failed.",
        },
    )()

    fake_client = type(
        "Client",
        (),
        {
            "connection_status": lambda self: fake_connection,
        },
    )()

    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "sap",
        },
        clear=True,
    ):
        with patch(
            "app.services.calm_source_status.SapCloudAlmClient."
            "from_environment",
            return_value=fake_client,
        ):
            result = get_calm_source_status()

    assert result.data_source == CalmDataSource.SAP
    assert result.configured is True
    assert result.authenticated is False
    assert result.connection_status == (
        CalmConnectionStatus.AUTHENTICATION_FAILED
    )


def test_unknown_source_falls_back_to_synthetic_status():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "unknown",
        },
        clear=True,
    ):
        result = get_calm_source_status()

    assert result.data_source == CalmDataSource.SYNTHETIC
    assert result.configured is True


def test_status_does_not_expose_secret():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "synthetic",
            "SAP_CALM_CLIENT_SECRET": "super-secret",
        },
        clear=True,
    ):
        result = get_calm_source_status()

    assert "super-secret" not in result.model_dump_json()
