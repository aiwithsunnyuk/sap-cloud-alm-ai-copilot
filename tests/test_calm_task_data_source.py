from unittest.mock import Mock, patch

import pytest

from app.models.calm_data_source import CalmDataSource
from app.services.calm_task_data_source import (
    SapCloudAlmTaskDataSource,
    SyntheticTaskDataSource,
    get_task_data_source,
)


def test_default_data_source_is_synthetic():
    with patch.dict(
        "os.environ",
        {},
        clear=True,
    ):
        source = get_task_data_source()

    assert isinstance(source, SyntheticTaskDataSource)


def test_environment_can_select_synthetic_source():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "synthetic",
        },
        clear=True,
    ):
        source = get_task_data_source()

    assert isinstance(source, SyntheticTaskDataSource)


def test_enum_can_select_synthetic_source():
    source = get_task_data_source(
        CalmDataSource.SYNTHETIC
    )

    assert isinstance(source, SyntheticTaskDataSource)


def test_unknown_data_source_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported SAP Cloud ALM data source",
    ):
        get_task_data_source("oracle")


def test_sap_source_requires_credentials():
    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "sap",
        },
        clear=True,
    ):
        with patch(
            "app.services.calm_task_data_source.SapCloudAlmClient."
            "from_environment",
            return_value=None,
        ):
            with pytest.raises(
                RuntimeError,
                match="credentials are not configured",
            ):
                get_task_data_source()


def test_sap_source_builds_sap_data_source():
    fake_client = Mock()

    with patch.dict(
        "os.environ",
        {
            "SAP_CALM_DATA_SOURCE": "sap",
        },
        clear=True,
    ):
        with patch(
            "app.services.calm_task_data_source.SapCloudAlmClient."
            "from_environment",
            return_value=fake_client,
        ):
            source = get_task_data_source()

    assert isinstance(source, SapCloudAlmTaskDataSource)
    assert source.client is fake_client


def test_synthetic_source_preserves_existing_tasks():
    source = SyntheticTaskDataSource()

    tasks = source.get_tasks(
        limit=2,
    )

    assert len(tasks) == 2
    assert tasks[0]["task_id"] == "TASK-001"


def test_synthetic_source_filters_project():
    source = SyntheticTaskDataSource()

    tasks = source.get_tasks(
        project_id="PRJ-001",
    )

    assert tasks
    assert all(
        task["project_id"] == "PRJ-001"
        for task in tasks
    )


def test_synthetic_source_applies_limit_after_filter():
    source = SyntheticTaskDataSource()

    tasks = source.get_tasks(
        project_id="PRJ-001",
        limit=1,
    )

    assert len(tasks) == 1


def test_sap_source_delegates_to_adapter(monkeypatch):
    fake_client = Mock()

    expected = [
        {
            "task_id": "TASK-001",
            "name": "Configure General Ledger",
        }
    ]

    monkeypatch.setattr(
        "app.services.calm_task_data_source.fetch_and_adapt_tasks",
        lambda client, **kwargs: expected,
    )

    source = SapCloudAlmTaskDataSource(fake_client)

    result = source.get_tasks(
        project_id="PRJ-001",
        limit=25,
    )

    assert result == expected


def test_sap_source_passes_client_and_filters():
    fake_client = Mock()

    with patch(
        "app.services.calm_task_data_source.fetch_and_adapt_tasks",
        return_value=[],
    ) as fetch_mock:
        source = SapCloudAlmTaskDataSource(fake_client)

        source.get_tasks(
            project_id="PRJ-001",
            limit=10,
        )

    fetch_mock.assert_called_once_with(
        fake_client,
        project_id="PRJ-001",
        limit=10,
    )
