from typing import Any

from app.models.calm_data_source import CalmDataSource
from app.services.calm_task_data_source import (
    get_task_data_source,
)


def retrieve_calm_tasks(
    *,
    project_id: str | None = None,
    limit: int | None = None,
) -> tuple[CalmDataSource, list[dict[str, Any]]]:
    source = get_task_data_source(CalmDataSource.SAP)

    tasks = source.get_tasks(
        project_id=project_id,
        limit=limit,
    )

    return CalmDataSource.SAP, tasks
