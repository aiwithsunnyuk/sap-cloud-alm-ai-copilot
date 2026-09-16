from app.services.intelligence_service import generate_operational_intelligence


def test_operational_intelligence_returns_control_tower_status():
    result = generate_operational_intelligence()

    assert result.overall_status == "Critical"
    assert result.total_insights == 6


def test_operational_intelligence_contains_critical_and_high_insights():
    result = generate_operational_intelligence()

    assert result.critical_insights == 2
    assert result.high_insights == 4


def test_operational_intelligence_has_required_evidence_and_actions():
    result = generate_operational_intelligence()

    assert result.insights

    for insight in result.insights:
        assert insight.insight_id
        assert insight.category
        assert insight.title
        assert insight.summary
        assert insight.evidence
        assert insight.recommended_action
