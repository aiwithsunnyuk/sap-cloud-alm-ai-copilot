from datetime import date

from app.services.risk_engine import calculate_risk_score


def test_blocked_critical_task_has_high_risk():
    task = {
        "task_id": "TASK-TEST-001",
        "workstream_id": "WS-INT",
        "name": "Integration Testing",
        "owner": "Integration Team",
        "status": "Blocked",
        "priority": "Critical",
        "planned_end": "2026-09-20",
        "percent_complete": 20,
    }

    dependencies = [
        {
            "dependency_id": "DEP-TEST-001",
            "from_task": "TASK-TEST-000",
            "to_task": "TASK-TEST-001",
            "type": "Blocks",
            "status": "Open",
        }
    ]

    risks = [
        {
            "risk_id": "RISK-TEST-001",
            "workstream_id": "WS-INT",
            "title": "Test environment unavailable",
            "severity": "Critical",
            "status": "Open",
        }
    ]

    result = calculate_risk_score(
        task=task,
        dependencies=dependencies,
        risks=risks,
        as_of_date=date(2026, 9, 7),
    )

    assert result["risk_level"] == "Critical"
    assert result["risk_score"] >= 75
    assert len(result["reasons"]) >= 3


def test_completed_task_has_low_risk():
    task = {
        "task_id": "TASK-TEST-002",
        "workstream_id": "WS-FIN",
        "name": "Completed Configuration",
        "owner": "Finance Team",
        "status": "Completed",
        "priority": "Low",
        "planned_end": "2026-09-01",
        "percent_complete": 100,
    }

    result = calculate_risk_score(
        task=task,
        dependencies=[],
        risks=[],
        as_of_date=date(2026, 9, 7),
    )

    assert result["risk_score"] == 5
    assert result["risk_level"] == "Low"


def test_risk_summary_contains_expected_structure():
    from app.services.project_service import get_risk_summary

    summary = get_risk_summary()

    assert summary["project_id"] == "PRJ-001"
    assert summary["total_tasks"] == 7

    distribution = summary["risk_distribution"]

    assert sum(distribution.values()) == 7
    assert len(summary["top_risks"]) == 3
