from typing import Any

from app.services.sap_cloud_alm_client import SapCloudAlmClient


SAP_TASK_RESOURCE = "/calm-Tasks/v1/Tasks"


_DEFAULT_STATUS_MAP = {
    "CIPTKOPEN": "In Progress",
    "OPEN": "In Progress",
    "IN_PROGRESS": "In Progress",
    "COMPLETED": "Completed",
    "CLOSED": "Completed",
}


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def _map_status(value: Any, status_map: dict[str, str] | None = None) -> str:
    if value is None:
        return "In Progress"

    raw = str(value)

    mapping = {
        **_DEFAULT_STATUS_MAP,
        **(status_map or {}),
    }

    return mapping.get(raw, raw)


def _map_priority(
    value: Any,
    priority_map: dict[int, str] | None = None,
) -> str:
    if value is None:
        return "Medium"

    if isinstance(value, str):
        return value

    if priority_map and value in priority_map:
        return priority_map[value]

    # Preserve an unmapped SAP priority rather than silently
    # inventing a business priority.
    return f"SAP_PRIORITY_{value}"


def _map_percent_complete(task: dict[str, Any]) -> int:
    value = _first_non_empty(
        task.get("percentComplete"),
        task.get("completionPercentage"),
        task.get("completion"),
    )

    if value is None:
        return 0

    try:
        return max(0, min(100, int(float(value))))
    except (TypeError, ValueError):
        return 0


def _map_workstream(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        parts = [
            part.strip()
            for part in value.split(",")
            if part.strip()
        ]
        return parts[0] if parts else ""

    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()

    return ""


def map_sap_task_to_internal(
    task: dict[str, Any],
    *,
    priority_map: dict[int, str] | None = None,
    status_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not isinstance(task, dict):
        raise ValueError("SAP task payload must be a dictionary.")

    task_id = _first_non_empty(
        task.get("externalId"),
        task.get("displayId"),
        task.get("id"),
    )

    name = _first_non_empty(
        task.get("title"),
        task.get("name"),
    )

    if not task_id:
        raise ValueError("SAP task payload is missing an identifiable task ID.")

    if not name:
        raise ValueError(
            f"SAP task {task_id} is missing a title."
        )

    owner = _first_non_empty(
        task.get("owner"),
        task.get("ownerName"),
        task.get("assigneeName"),
        task.get("assigneeId"),
    )

    return {
        "name": str(name),
        "owner": str(owner or ""),
        "percent_complete": _map_percent_complete(task),
        "planned_end": task.get("dueDate"),
        "planned_start": task.get("startDate"),
        "priority": _map_priority(
            _first_non_empty(
                task.get("priority"),
                task.get("priorityId"),
            ),
            priority_map=priority_map,
        ),
        "project_id": _first_non_empty(
            task.get("projectId"),
            task.get("scopeId"),
        ),
        "status": _map_status(
            task.get("status"),
            status_map=status_map,
        ),
        "task_id": str(task_id),
        "workstream_id": _map_workstream(
            task.get("workstream")
        ),
    }


def adapt_sap_task_collection(
    payload: dict[str, Any] | list[dict[str, Any]],
    *,
    priority_map: dict[int, str] | None = None,
    status_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        tasks = payload.get("value", payload.get("tasks"))

        if tasks is None:
            raise ValueError(
                "SAP task collection dictionary must contain "
                "'value' or 'tasks'."
            )
    elif isinstance(payload, list):
        tasks = payload
    else:
        raise ValueError(
            "SAP task collection must be a list or dictionary."
        )

    if not isinstance(tasks, list):
        raise ValueError("SAP task collection items must be a list.")

    return [
        map_sap_task_to_internal(
            task,
            priority_map=priority_map,
            status_map=status_map,
        )
        for task in tasks
    ]


def fetch_and_adapt_tasks(
    client: SapCloudAlmClient,
    *,
    project_id: str | None = None,
    limit: int | None = None,
    priority_map: dict[int, str] | None = None,
    status_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}

    if project_id:
        params["projectId"] = project_id

    if limit is not None:
        params["limit"] = limit

    payload = client.get(
        SAP_TASK_RESOURCE,
        params=params or None,
    )

    return adapt_sap_task_collection(
        payload,
        priority_map=priority_map,
        status_map=status_map,
    )
