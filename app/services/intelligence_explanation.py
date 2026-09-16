from app.models.intelligence_explanation import (
    ExplanationResponse,
    OperationalExplanation,
)
from app.services.intelligence_correlation import (
    generate_operational_correlations,
)


def generate_operational_explanations() -> ExplanationResponse:
    correlation_result = generate_operational_correlations()

    explanations: list[OperationalExplanation] = []

    for correlation in correlation_result.correlations:
        chain = correlation.causal_chain
        chain_text = " → ".join(chain)

        if correlation.severity == "Critical":
            impact = (
                "The correlated chain contains a critical operational "
                "condition and should be reviewed before further "
                "delivery activity proceeds."
            )
        elif correlation.severity == "High":
            impact = (
                "The correlated chain indicates elevated operational "
                "risk that may affect delivery or service stability."
            )
        else:
            impact = (
                "The correlated chain indicates an operational condition "
                "that should remain under review."
            )

        explanations.append(
            OperationalExplanation(
                explanation_id=f"EXP-{correlation.correlation_id}",
                severity=correlation.severity,
                title=(
                    f"Operational explanation for "
                    f"{correlation.correlation_id}"
                ),
                what_happened=(
                    "Multiple operational records were linked across "
                    f"the following chain: {chain_text}."
                ),
                why_it_matters=(
                    "The correlation connects operational signals with "
                    "downstream incident, problem, change, release, "
                    "or deployment activity, providing traceable "
                    "evidence for the current condition."
                ),
                operational_impact=impact,
                evidence=correlation.evidence,
                recommended_review=(
                    "Review the correlated objects and supporting evidence "
                    "before approving additional implementation, release, "
                    "or deployment activity."
                ),
            )
        )

    critical_count = sum(
        1 for item in explanations if item.severity == "Critical"
    )
    high_count = sum(
        1 for item in explanations if item.severity == "High"
    )

    return ExplanationResponse(
        overall_status=correlation_result.overall_status,
        total_explanations=len(explanations),
        critical_explanations=critical_count,
        high_explanations=high_count,
        explanations=explanations,
    )
