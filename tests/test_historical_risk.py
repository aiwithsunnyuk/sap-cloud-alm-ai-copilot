from app.services.historical_risk import (
    get_task_history,
    load_risk_history,
)


def test_risk_history_contains_expected_snapshots():
    history = load_risk_history()

    assert len(history) == 35
    assert history[0]["task_id"] == "TASK-001"


def test_task_history_is_chronological():
    history = get_task_history("TASK-006")

    assert len(history) == 5
    assert history[0]["snapshot_date"] == "2026-09-11"
    assert history[-1]["snapshot_date"] == "2026-09-15"


def test_task_006_risk_increased():
    history = get_task_history("TASK-006")

    assert history[0]["risk_score"] == 58
    assert history[-1]["risk_score"] == 100


def test_unknown_task_returns_empty_history():
    history = get_task_history("TASK-999")

    assert history == []
