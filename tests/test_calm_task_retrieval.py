from unittest.mock import Mock, patch

import pytest

from app.models.calm_data_source import CalmDataSource
from app.services.calm_task_retrieval import (
    retrieve_calm_tasks,
)


def test_retrieval_explicitly_selects_sap_source():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
            "task_id": "TASK-001",
            "name": "Configure General Ledger",
        }
    ]

    with patch(
        "app.services.calm_task_retrieval.get_task_data_source",
        return_value=fake_source,
    ) as factory:
        source, tasks = retrieve_calm_tasks(
            project_id="PRJ-001",
            limit=10,
        )

    factory.assert_called_once_with(
        CalmDataSource.SAP
    )

    fake_source.get_tasks.assert_called_once_with(
        project_id="PRJ-001",
        limit=10,
    )

    assert source == CalmDataSource.SAP
    assert tasks == [
        {
            "task_id": "TASK-001",
            "name": "Configure General Ledger",
        }
    ]


def test_retrieval_returns_empty_sap_result():
    fake_source = Mock()
    fake_source.get_tasks.return_value = []

    with patch(
        "app.services.calm_task_retrieval.get_task_data_source",
        return_value=fake_source,
    ):
        source, tasks = retrieve_calm_tasks()

    assert source == CalmDataSource.SAP
    assert tasks == []


def test_retrieval_propagates_missing_sap_credentials():
    with patch(
        "app.services.calm_task_retrieval.get_task_data_source",
        side_effect=RuntimeError(
            "SAP Cloud ALM data source was requested, "
            "but SAP Cloud ALM credentials are not configured."
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="credentials are not configured",
        ):
            retrieve_calm_tasks()


def test_retrieval_preserves_internal_task_contract():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
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
    ]

    with patch(
        "app.services.calm_task_retrieval.get_task_data_source",
        return_value=fake_source,
    ):
        _, tasks = retrieve_calm_tasks()

    assert set(tasks[0]) == {
        "name",
        "owner",
        "percent_complete",
        "planned_end",
        "planned_start",
        "priority",
        "project_id",
        "status",
        "task_id",
        "workstream_id",
    }
