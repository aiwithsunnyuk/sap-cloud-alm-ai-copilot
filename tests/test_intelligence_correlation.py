from app.services.intelligence_correlation import (
    generate_operational_correlations,
)


def test_operational_correlations_detect_incident_chains():
    result = generate_operational_correlations()

    assert result.total_correlations > 0
    assert result.overall_status == "Critical"


def test_operational_correlation_contains_downstream_chain():
    result = generate_operational_correlations()

    correlation = next(
        item
        for item in result.correlations
        if item.correlation_id == "COR-INC-003"
    )

    assert "INC-003" in correlation.causal_chain
    assert "PRB-001" in correlation.causal_chain
    assert "CHG-001" in correlation.causal_chain
    assert "REL-001" in correlation.causal_chain
    assert "DEP-001" in correlation.causal_chain


def test_operational_correlation_has_evidence_and_action():
    result = generate_operational_correlations()

    assert result.correlations

    for correlation in result.correlations:
        assert correlation.related_objects
        assert correlation.causal_chain
        assert correlation.evidence
        assert correlation.recommended_action
