from unittest.mock import Mock, patch

from app.models.calm_data_source import CalmDataSource
from app.services.task_service import (
    get_application_task,
    get_application_tasks,
)


def test_application_tasks_default_to_configured_data_source():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
            "task_id": "TASK-001",
            "name": "Configure General Ledger",
        }
    ]

    with patch(
        "app.services.task_service.get_task_data_source",
        return_value=fake_source,
    ) as factory:
        result = get_application_tasks()

    factory.assert_called_once_with(None)

    fake_source.get_tasks.assert_called_once_with(
        project_id=None,
        limit=None,
    )

    assert result[0]["task_id"] == "TASK-001"


def test_application_tasks_pass_project_and_limit():
    fake_source = Mock()

    fake_source.get_tasks.return_value = []

    with patch(
        "app.services.task_service.get_task_data_source",
        return_value=fake_source,
    ):
        result = get_application_tasks(
            project_id="PRJ-001",
            limit=10,
        )

    assert result == []

    fake_source.get_tasks.assert_called_once_with(
        project_id="PRJ-001",
        limit=10,
    )


def test_application_tasks_can_select_synthetic_mode():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
            "task_id": "TASK-001",
        }
    ]

    with patch(
        "app.services.task_service.get_task_data_source",
        return_value=fake_source,
    ) as factory:
        result = get_application_tasks(
            mode=CalmDataSource.SYNTHETIC,
        )

    factory.assert_called_once_with(
        CalmDataSource.SYNTHETIC
    )

    assert result == [
        {
            "task_id": "TASK-001",
        }
    ]


def test_application_task_returns_matching_task():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
            "task_id": "TASK-001",
            "name": "Configure General Ledger",
        },
        {
            "task_id": "TASK-002",
            "name": "Configure Accounts Payable",
        },
    ]

    with patch(
        "app.services.task_service.get_task_data_source",
        return_value=fake_source,
    ):
        result = get_application_task("TASK-002")

    assert result == {
        "task_id": "TASK-002",
        "name": "Configure Accounts Payable",
    }


def test_application_task_returns_none_when_not_found():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
            "task_id": "TASK-001",
        }
    ]

    with patch(
        "app.services.task_service.get_task_data_source",
        return_value=fake_source,
    ):
        result = get_application_task("TASK-999")

    assert result is None


def test_application_task_passes_selected_mode():
    fake_source = Mock()

    fake_source.get_tasks.return_value = [
        {
            "task_id": "TASK-001",
        }
    ]

    with patch(
        "app.services.task_service.get_task_data_source",
        return_value=fake_source,
    ) as factory:
        result = get_application_task(
            "TASK-001",
            mode="synthetic",
        )

    factory.assert_called_once_with("synthetic")
    assert result["task_id"] == "TASK-001"
