from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app
from app.models.calm_data_source import CalmDataSource


client = TestClient(app)


def test_calm_tasks_endpoint_returns_sap_tasks():
    with patch(
        "app.api.retrieve_calm_tasks",
        return_value=(
            CalmDataSource.SAP,
            [
                {
                    "task_id": "TASK-001",
                    "name": "Configure General Ledger",
                },
                {
                    "task_id": "TASK-002",
                    "name": "Configure Accounts Payable",
                },
            ],
        ),
    ):
        response = client.get(
            "/integration/calm/tasks"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["data_source"] == "sap"
    assert body["count"] == 2
    assert len(body["tasks"]) == 2
    assert body["tasks"][0]["task_id"] == "TASK-001"


def test_calm_tasks_endpoint_passes_filters():
    with patch(
        "app.api.retrieve_calm_tasks",
        return_value=(
            CalmDataSource.SAP,
            [],
        ),
    ) as retrieve:

        response = client.get(
            "/integration/calm/tasks",
            params={
                "project_id": "PRJ-001",
                "limit": 25,
            },
        )

    assert response.status_code == 200

    retrieve.assert_called_once_with(
        project_id="PRJ-001",
        limit=25,
    )


def test_calm_tasks_endpoint_returns_sap_source():
    with patch(
        "app.api.retrieve_calm_tasks",
        return_value=(
            CalmDataSource.SAP,
            [],
        ),
    ):
        response = client.get(
            "/integration/calm/tasks"
        )

    assert response.status_code == 200
    assert response.json()["data_source"] == "sap"
