from unittest.mock import patch

import requests

from app.models.calm_connection import (
    CalmConnectionConfig,
    CalmConnectionStatus,
)
from app.services.sap_cloud_alm_client import (
    SapCloudAlmClient,
)


def _config():
    return CalmConnectionConfig(
        api_base_url="https://tenant.eu10.alm.cloud.sap/api",
        token_url="https://uaa.example.com/oauth/token",
        client_id="client-id",
        client_secret="client-secret",
    )


@patch("app.services.sap_cloud_alm_client.requests.post")
def test_get_access_token_uses_client_credentials(mock_post):
    mock_post.return_value.json.return_value = {
        "access_token": "token-123",
        "token_type": "bearer",
    }
    mock_post.return_value.raise_for_status.return_value = None

    client = SapCloudAlmClient(_config())

    token = client.get_access_token()

    assert token == "token-123"

    mock_post.assert_called_once_with(
        "https://uaa.example.com/oauth/token",
        data={
            "grant_type": "client_credentials",
        },
        auth=("client-id", "client-secret"),
        timeout=20,
    )


@patch("app.services.sap_cloud_alm_client.requests.post")
def test_connection_status_is_authenticated(mock_post):
    mock_post.return_value.json.return_value = {
        "access_token": "token-123",
    }
    mock_post.return_value.raise_for_status.return_value = None

    client = SapCloudAlmClient(_config())

    result = client.connection_status()

    assert result.status == CalmConnectionStatus.AUTHENTICATED
    assert result.authenticated is True
    assert result.api_base_url == (
        "https://tenant.eu10.alm.cloud.sap/api"
    )


@patch("app.services.sap_cloud_alm_client.requests.post")
def test_connection_status_handles_authentication_failure(mock_post):
    mock_post.side_effect = requests.RequestException(
        "token endpoint unavailable"
    )

    client = SapCloudAlmClient(_config())

    result = client.connection_status()

    assert result.status == CalmConnectionStatus.AUTHENTICATION_FAILED
    assert result.authenticated is False
    assert "authentication failed" in result.message.lower()


@patch("app.services.sap_cloud_alm_client.requests.post")
@patch("app.services.sap_cloud_alm_client.requests.get")
def test_get_uses_bearer_token(mock_get, mock_post):
    mock_post.return_value.json.return_value = {
        "access_token": "token-123",
    }
    mock_post.return_value.raise_for_status.return_value = None

    mock_get.return_value.json.return_value = {
        "value": [
            {
                "id": "TASK-001",
            }
        ]
    }
    mock_get.return_value.raise_for_status.return_value = None

    client = SapCloudAlmClient(_config())

    result = client.get("/calm-Tasks/v1/Tasks")

    assert result == {
        "value": [
            {
                "id": "TASK-001",
            }
        ]
    }

    mock_get.assert_called_once_with(
        "https://tenant.eu10.alm.cloud.sap/api/"
        "calm-Tasks/v1/Tasks",
        headers={
            "Authorization": "Bearer token-123",
            "Accept": "application/json",
        },
        params=None,
        timeout=30,
    )


@patch("app.services.sap_cloud_alm_client.requests.post")
def test_missing_access_token_is_rejected(mock_post):
    mock_post.return_value.json.return_value = {}
    mock_post.return_value.raise_for_status.return_value = None

    client = SapCloudAlmClient(_config())

    try:
        client.get_access_token()
        assert False, "Expected RuntimeError was not raised."
    except RuntimeError as exc:
        assert "access_token" in str(exc)


def test_environment_without_credentials_returns_none():
    with patch.dict(
        "os.environ",
        {},
        clear=True,
    ):
        client = SapCloudAlmClient.from_environment()

    assert client is None


def test_environment_builds_configured_client():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_API_BASE_URL": (
                "https://tenant.eu10.alm.cloud.sap/api/"
            ),
            "SAP_CALM_TOKEN_URL": (
                "https://uaa.example.com/oauth/token"
            ),
            "SAP_CALM_CLIENT_ID": "client-id",
            "SAP_CALM_CLIENT_SECRET": "client-secret",
        },
        clear=True,
    ):
        client = SapCloudAlmClient.from_environment()

    assert client is not None
    assert client.config.api_base_url == (
        "https://tenant.eu10.alm.cloud.sap/api"
    )
    assert client.config.client_id == "client-id"
