from unittest.mock import Mock

import pytest

from app.services.calm_task_adapter import (
    SAP_TASK_RESOURCE,
    adapt_sap_task_collection,
    fetch_and_adapt_tasks,
    map_sap_task_to_internal,
)


def _sap_task():
    return {
        "title": "Configure General Ledger",
        "externalId": "TASK-001",
        "startDate": "2026-08-15",
        "dueDate": "2026-09-05",
        "priorityId": 2,
        "assigneeId": "FIN-001",
        "assigneeName": "Finance Team",
        "description": "Configure the ledger.",
        "workstream": "WS-FIN,WS-INT",
        "projectId": "PRJ-001",
        "status": "CIPTKOPEN",
        "percentComplete": 70,
    }


def test_maps_sap_task_to_internal_contract():
    result = map_sap_task_to_internal(
        _sap_task(),
        priority_map={
            0: "Low",
            1: "Medium",
            2: "High",
        },
    )

    assert result == {
        "name": "Configure General Ledger",
        "owner": "Finance Team",
        "percent_complete": 70,
        "planned_end": "2026-09-05",
        "planned_start": "2026-08-15",
        "priority": "High",
        "project_id": "PRJ-001",
        "status": "In Progress",
        "task_id": "TASK-001",
        "workstream_id": "WS-FIN",
    }


def test_owner_falls_back_to_assignee_id():
    task = _sap_task()

    task.pop("assigneeName")

    result = map_sap_task_to_internal(task)

    assert result["owner"] == "FIN-001"


def test_numeric_priority_can_be_mapped_without_hardcoding_semantics():
    result = map_sap_task_to_internal(
        _sap_task(),
        priority_map={
            2: "High",
        },
    )

    assert result["priority"] == "High"


def test_unmapped_numeric_priority_is_preserved():
    result = map_sap_task_to_internal(_sap_task())

    assert result["priority"] == "SAP_PRIORITY_2"


def test_workstream_uses_first_value_from_sap_list():
    task = _sap_task()
    task["workstream"] = ["WS-PROC", "WS-SALES"]

    result = map_sap_task_to_internal(task)

    assert result["workstream_id"] == "WS-PROC"


def test_task_collection_accepts_sap_list():
    result = adapt_sap_task_collection(
        [_sap_task()],
        priority_map={2: "High"},
    )

    assert len(result) == 1
    assert result[0]["task_id"] == "TASK-001"
    assert result[0]["priority"] == "High"


def test_task_collection_accepts_value_envelope():
    result = adapt_sap_task_collection(
        {
            "value": [
                _sap_task(),
            ]
        },
        priority_map={2: "High"},
    )

    assert len(result) == 1
    assert result[0]["task_id"] == "TASK-001"


def test_task_collection_accepts_tasks_envelope():
    result = adapt_sap_task_collection(
        {
            "tasks": [
                _sap_task(),
            ]
        },
        priority_map={2: "High"},
    )

    assert len(result) == 1
    assert result[0]["task_id"] == "TASK-001"


def test_missing_task_id_is_rejected():
    task = _sap_task()
    task.pop("externalId")
    task.pop("id", None)
    task.pop("displayId", None)

    with pytest.raises(ValueError, match="missing an identifiable task ID"):
        map_sap_task_to_internal(task)


def test_missing_title_is_rejected():
    task = _sap_task()
    task.pop("title")

    with pytest.raises(ValueError, match="missing a title"):
        map_sap_task_to_internal(task)


def test_invalid_percent_complete_defaults_safely():
    task = _sap_task()
    task["percentComplete"] = "not-a-number"

    result = map_sap_task_to_internal(task)

    assert result["percent_complete"] == 0


def test_fetch_and_adapt_calls_sap_task_api():
    client = Mock()

    client.get.return_value = {
        "value": [
            _sap_task(),
        ]
    }

    result = fetch_and_adapt_tasks(
        client,
        project_id="PRJ-001",
        limit=30,
        priority_map={2: "High"},
    )

    assert result[0]["task_id"] == "TASK-001"

    client.get.assert_called_once_with(
        SAP_TASK_RESOURCE,
        params={
            "projectId": "PRJ-001",
            "limit": 30,
        },
    )
