import os

import requests

from app.models.calm_connection import (
    CalmConnectionConfig,
    CalmConnectionResult,
    CalmConnectionStatus,
)


class SapCloudAlmClient:
    def __init__(self, config: CalmConnectionConfig):
        self.config = config
        self._access_token: str | None = None

    @classmethod
    def from_environment(cls) -> "SapCloudAlmClient | None":
        api_base_url = os.getenv("SAP_CALM_API_BASE_URL", "").strip()
        token_url = os.getenv("SAP_CALM_TOKEN_URL", "").strip()
        client_id = os.getenv("SAP_CALM_CLIENT_ID", "").strip()
        client_secret = os.getenv("SAP_CALM_CLIENT_SECRET", "").strip()

        if not all(
            [
                api_base_url,
                token_url,
                client_id,
                client_secret,
            ]
        ):
            return None

        return cls(
            CalmConnectionConfig(
                api_base_url=api_base_url.rstrip("/"),
                token_url=token_url,
                client_id=client_id,
                client_secret=client_secret,
            )
        )

    def get_access_token(self) -> str:
        response = requests.post(
            self.config.token_url,
            data={
                "grant_type": "client_credentials",
            },
            auth=(
                self.config.client_id,
                self.config.client_secret,
            ),
            timeout=20,
        )

        response.raise_for_status()

        payload = response.json()
        token = payload.get("access_token")

        if not isinstance(token, str) or not token:
            raise RuntimeError(
                "SAP Cloud ALM token response did not contain access_token."
            )

        self._access_token = token

        return token

    def connection_status(self) -> CalmConnectionResult:
        if not self.config:
            return CalmConnectionResult(
                status=CalmConnectionStatus.NOT_CONFIGURED,
                authenticated=False,
                api_base_url="",
                message="SAP Cloud ALM credentials are not configured.",
            )

        try:
            self.get_access_token()

        except requests.RequestException as exc:
            return CalmConnectionResult(
                status=CalmConnectionStatus.AUTHENTICATION_FAILED,
                authenticated=False,
                api_base_url=self.config.api_base_url,
                message=f"SAP Cloud ALM authentication failed: {exc}",
            )

        return CalmConnectionResult(
            status=CalmConnectionStatus.AUTHENTICATED,
            authenticated=True,
            api_base_url=self.config.api_base_url,
            message="SAP Cloud ALM OAuth authentication succeeded.",
        )

    def get(
        self,
        resource_path: str,
        params: dict | None = None,
    ) -> dict | list:
        token = self._access_token or self.get_access_token()

        path = resource_path.lstrip("/")
        url = f"{self.config.api_base_url}/{path}"

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()
