from app.services.intelligence_recommendation import (
    generate_operational_recommendations,
)


def test_operational_recommendations_have_priorities():
    result = generate_operational_recommendations()

    assert result.overall_status == "Critical"
    assert result.total_recommendations > 0
    assert result.p1_recommendations > 0
    assert result.p2_recommendations > 0


def test_recommendations_are_sorted_by_priority():
    result = generate_operational_recommendations()

    scores = [
        item.priority_score
        for item in result.recommendations
    ]

    assert scores == sorted(scores, reverse=True)


def test_recommendation_contains_action_rationale_and_evidence():
    result = generate_operational_recommendations()

    for recommendation in result.recommendations:
        assert recommendation.recommendation_id
        assert recommendation.priority
        assert recommendation.priority_score > 0
        assert recommendation.action
        assert recommendation.rationale
        assert recommendation.evidence
        assert recommendation.source_explanation
