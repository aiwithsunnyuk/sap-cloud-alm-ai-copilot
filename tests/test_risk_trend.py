from app.services.risk_trend import calculate_risk_trend


def test_task_006_is_deteriorating():
    result = calculate_risk_trend("TASK-006")

    assert result["snapshot_count"] == 5
    assert result["starting_risk_score"] == 58
    assert result["current_risk_score"] == 100
    assert result["risk_change"] == 42
    assert result["risk_velocity"] == 10.5
    assert result["trend"] == "Deteriorating"
    assert result["severity_transition"] == "High → Critical"


def test_task_003_is_improving():
    result = calculate_risk_trend("TASK-003")

    assert result["starting_risk_score"] == 28
    assert result["current_risk_score"] == 18
    assert result["risk_change"] == -10
    assert result["trend"] == "Improving"


def test_task_004_is_stable():
    result = calculate_risk_trend("TASK-004")

    assert result["starting_risk_score"] == 35
    assert result["current_risk_score"] == 33
    assert result["risk_change"] == -2
    assert result["trend"] == "Stable"


def test_unknown_task_has_no_data():
    result = calculate_risk_trend("TASK-999")

    assert result["snapshot_count"] == 0
    assert result["trend"] == "No Data"
