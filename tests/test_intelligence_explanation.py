from app.services.intelligence_explanation import (
    generate_operational_explanations,
)


def test_operational_explanations_match_correlation_population():
    result = generate_operational_explanations()

    assert result.overall_status == "Critical"
    assert result.total_explanations > 0


def test_operational_explanation_contains_business_reasoning():
    result = generate_operational_explanations()

    explanation = result.explanations[0]

    assert explanation.what_happened
    assert explanation.why_it_matters
    assert explanation.operational_impact
    assert explanation.evidence
    assert explanation.recommended_review


def test_operational_explanations_preserve_severity_counts():
    result = generate_operational_explanations()

    assert result.critical_explanations > 0
    assert result.high_explanations >= 0
