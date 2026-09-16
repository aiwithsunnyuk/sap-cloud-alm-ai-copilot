from app.services.intelligence_decision_brief import (
    generate_operational_decision_brief,
)


def test_decision_brief_has_current_operational_status():
    result = generate_operational_decision_brief()

    assert result.overall_status == "Critical"
    assert result.brief_id == "BRIEF-001"
    assert result.total_risks > 0


def test_decision_brief_contains_priority_actions():
    result = generate_operational_decision_brief()

    assert result.priority_actions_count > 0
    assert result.priority_actions


def test_decision_brief_contains_decision_points_and_evidence():
    result = generate_operational_decision_brief()

    assert result.decision_points
    assert result.evidence


def test_decision_brief_contains_affected_scope():
    result = generate_operational_decision_brief()

    assert result.affected_components
    assert result.affected_workstreams
