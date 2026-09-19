from datetime import date

from app.services.calm_risk_evaluation import (
    evaluate_sap_task_risk,
)
from app.services.risk_engine import calculate_risk_score


def _sap_task():
    return {
        "title": "Configure General Ledger",
        "externalId": "TASK-001",
        "startDate": "2026-08-15",
        "dueDate": "2026-09-05",
        "priorityId": 2,
        "assigneeName": "Finance Team",
        "projectId": "PRJ-001",
        "status": "CIPTKOPEN",
        "percentComplete": 70,
        "workstream": "WS-FIN",
    }


def _priority_map():
    return {
        0: "Low",
        1: "Medium",
        2: "High",
    }


def test_sap_task_is_evaluated_through_existing_risk_engine():
    result = evaluate_sap_task_risk(
        _sap_task(),
        priority_map=_priority_map(),
        as_of_date=date(2026, 9, 7),
    )

    expected_task = {
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

    expected_risk = calculate_risk_score(
        task=expected_task,
        dependencies=[],
        risks=[],
        as_of_date=date(2026, 9, 7),
    )

    assert result["source"] == "sap_cloud_alm"
    assert result["task"] == expected_task
    assert result["risk"] == expected_risk


def test_sap_and_internal_task_produce_identical_risk():
    sap_result = evaluate_sap_task_risk(
        _sap_task(),
        priority_map=_priority_map(),
        as_of_date=date(2026, 9, 7),
    )

    internal_task = sap_result["task"]

    direct_result = calculate_risk_score(
        task=internal_task,
        dependencies=[],
        risks=[],
        as_of_date=date(2026, 9, 7),
    )

    assert sap_result["risk"] == direct_result


def test_sap_task_preserves_high_risk_signals():
    dependencies = [
        {
            "dependency_id": "DEP-SAP-001",
            "from_task": "TASK-000",
            "to_task": "TASK-001",
            "type": "Blocks",
            "status": "Open",
        }
    ]

    risks = [
        {
            "risk_id": "RISK-SAP-001",
            "workstream_id": "WS-FIN",
            "title": "Chart of Accounts approval delayed",
            "severity": "Critical",
            "status": "Open",
        }
    ]

    result = evaluate_sap_task_risk(
        _sap_task(),
        dependencies=dependencies,
        risks=risks,
        priority_map=_priority_map(),
        as_of_date=date(2026, 9, 7),
    )

    assert result["risk"]["risk_level"] == "Critical"
    assert result["risk"]["risk_score"] >= 75
    assert len(result["risk"]["reasons"]) >= 3


def test_sap_task_status_is_mapped_before_risk_evaluation():
    task = _sap_task()
    task["status"] = "COMPLETED"
    task["percentComplete"] = 100
    task["priority"] = "Low"

    result = evaluate_sap_task_risk(
        task,
        priority_map=_priority_map(),
        as_of_date=date(2026, 9, 7),
    )

    assert result["task"]["status"] == "Completed"
    assert result["risk"]["risk_score"] == 5
    assert result["risk"]["risk_level"] == "Low"


def test_sap_priority_mapping_changes_risk_deterministically():
    task = _sap_task()

    high_result = evaluate_sap_task_risk(
        task,
        priority_map={
            2: "High",
        },
        as_of_date=date(2026, 9, 7),
    )

    low_result = evaluate_sap_task_risk(
        task,
        priority_map={
            2: "Low",
        },
        as_of_date=date(2026, 9, 7),
    )

    assert high_result["task"]["priority"] == "High"
    assert low_result["task"]["priority"] == "Low"
    assert high_result["risk"]["risk_score"] > (
        low_result["risk"]["risk_score"]
    )


def test_sap_task_missing_optional_workstream_is_safe():
    task = _sap_task()
    task.pop("workstream")

    result = evaluate_sap_task_risk(
        task,
        priority_map=_priority_map(),
        as_of_date=date(2026, 9, 7),
    )

    assert result["task"]["workstream_id"] == ""
    assert result["risk"]["risk_score"] >= 0


def test_sap_task_source_is_explicitly_identified():
    result = evaluate_sap_task_risk(
        _sap_task(),
        priority_map=_priority_map(),
        as_of_date=date(2026, 9, 7),
    )

    assert result["source"] == "sap_cloud_alm"
    assert result["task"]["task_id"] == "TASK-001"
    assert "risk_score" in result["risk"]
    assert "risk_level" in result["risk"]
