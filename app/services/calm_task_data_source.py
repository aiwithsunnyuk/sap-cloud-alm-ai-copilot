import os
from typing import Any, Protocol

from app.models.calm_data_source import CalmDataSource
from app.services.calm_task_adapter import fetch_and_adapt_tasks
from app.services.project_service import get_tasks
from app.services.sap_cloud_alm_client import SapCloudAlmClient


class TaskDataSource(Protocol):
    def get_tasks(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        ...


class SyntheticTaskDataSource:
    """Existing JSON-backed task source."""

    def get_tasks(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        tasks = get_tasks()

        if project_id:
            tasks = [
                task
                for task in tasks
                if task.get("project_id") == project_id
            ]

        if limit is not None:
            tasks = tasks[:limit]

        return tasks


class SapCloudAlmTaskDataSource:
    """SAP Cloud ALM-backed task source."""

    def __init__(self, client: SapCloudAlmClient):
        self.client = client

    def get_tasks(
        self,
        *,
        project_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return fetch_and_adapt_tasks(
            self.client,
            project_id=project_id,
            limit=limit,
        )


def _resolve_mode(mode: str | CalmDataSource | None) -> CalmDataSource:
    raw_mode = mode or os.getenv(
        "SAP_CALM_DATA_SOURCE",
        CalmDataSource.SYNTHETIC.value,
    )

    if isinstance(raw_mode, CalmDataSource):
        return raw_mode

    normalized = str(raw_mode).strip().lower()

    try:
        return CalmDataSource(normalized)
    except ValueError as exc:
        raise ValueError(
            "Unsupported SAP Cloud ALM data source: "
            f"{raw_mode!r}. Expected 'synthetic' or 'sap'."
        ) from exc


def get_task_data_source(
    mode: str | CalmDataSource | None = None,
) -> TaskDataSource:
    source = _resolve_mode(mode)

    if source == CalmDataSource.SYNTHETIC:
        return SyntheticTaskDataSource()

    client = SapCloudAlmClient.from_environment()

    if client is None:
        raise RuntimeError(
            "SAP Cloud ALM data source was requested, but SAP Cloud ALM "
            "credentials are not configured."
        )

    return SapCloudAlmTaskDataSource(client)
