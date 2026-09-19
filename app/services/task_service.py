from typing import Any

from app.models.calm_data_source import CalmDataSource
from app.services.calm_task_data_source import get_task_data_source


def get_application_tasks(
    *,
    project_id: str | None = None,
    limit: int | None = None,
    mode: str | CalmDataSource | None = None,
) -> list[dict[str, Any]]:
    source = get_task_data_source(mode)

    return source.get_tasks(
        project_id=project_id,
        limit=limit,
    )


def get_application_task(
    task_id: str,
    *,
    mode: str | CalmDataSource | None = None,
) -> dict[str, Any] | None:
    tasks = get_application_tasks(mode=mode)

    for task in tasks:
        if task.get("task_id") == task_id:
            return task

    return None
