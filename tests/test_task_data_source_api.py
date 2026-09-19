from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_tasks_endpoint_uses_default_synthetic_source():
    response = client.get("/tasks")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) == 7
    assert body[0]["task_id"] == "TASK-001"


def test_tasks_endpoint_supports_project_filter():
    response = client.get(
        "/tasks",
        params={
            "project_id": "PRJ-001",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body
    assert all(
        task["project_id"] == "PRJ-001"
        for task in body
    )


def test_tasks_endpoint_supports_limit():
    response = client.get(
        "/tasks",
        params={
            "limit": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2


def test_tasks_endpoint_preserves_internal_task_contract():
    response = client.get("/tasks")

    assert response.status_code == 200

    task = response.json()[0]

    expected_fields = {
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

    assert expected_fields.issubset(task.keys())
