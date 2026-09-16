from app.models.intelligence_recommendation import (
    OperationalRecommendation,
    RecommendationResponse,
)
from app.services.intelligence_explanation import (
    generate_operational_explanations,
)


_PRIORITY_RULES = {
    "Critical": ("P1", 100),
    "High": ("P2", 75),
    "Medium": ("P3", 50),
    "Low": ("P4", 25),
}


def _priority_for_severity(severity: str) -> tuple[str, int]:
    return _PRIORITY_RULES.get(severity, ("P4", 25))


def generate_operational_recommendations() -> RecommendationResponse:
    explanation_result = generate_operational_explanations()

    recommendations: list[OperationalRecommendation] = []

    for explanation in explanation_result.explanations:
        priority, priority_score = _priority_for_severity(
            explanation.severity
        )

        recommendations.append(
            OperationalRecommendation(
                recommendation_id=f"REC-{explanation.explanation_id}",
                priority=priority,
                priority_score=priority_score,
                severity=explanation.severity,
                title=explanation.title,
                action=explanation.recommended_review,
                rationale=(
                    f"This recommendation is {priority} because the "
                    f"source explanation is classified as "
                    f"{explanation.severity}."
                ),
                evidence=explanation.evidence,
                source_explanation=explanation.explanation_id,
            )
        )

    recommendations.sort(
        key=lambda item: (
            -item.priority_score,
            item.recommendation_id,
        )
    )

    p1_count = sum(
        1 for item in recommendations if item.priority == "P1"
    )
    p2_count = sum(
        1 for item in recommendations if item.priority == "P2"
    )

    return RecommendationResponse(
        overall_status=explanation_result.overall_status,
        total_recommendations=len(recommendations),
        p1_recommendations=p1_count,
        p2_recommendations=p2_count,
        recommendations=recommendations,
    )
