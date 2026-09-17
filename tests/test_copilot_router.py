from app.models.copilot import CopilotIntent, CopilotQueryRequest
from app.services.copilot_router import classify_copilot_query


def test_project_health_query_routes_to_control_tower():
    result = classify_copilot_query(
        CopilotQueryRequest(
            question="What is the current project status?"
        )
    )

    assert result.intent == CopilotIntent.PROJECT_HEALTH
    assert result.target_capability == "Operations Control Tower"
    assert result.suggested_endpoint == "/operations/control-tower"
    assert result.confidence > 0


def test_rollback_query_routes_to_deployment_intelligence():
    result = classify_copilot_query(
        CopilotQueryRequest(
            question="Why was the deployment rolled back?"
        )
    )

    assert result.intent == CopilotIntent.DEPLOYMENT
    assert result.suggested_endpoint == "/deployments/summary"


def test_recommendation_query_routes_to_recommendations():
    result = classify_copilot_query(
        CopilotQueryRequest(
            question="What needs attention first?"
        )
    )

    assert result.intent == CopilotIntent.RECOMMENDATION
    assert result.suggested_endpoint == "/intelligence/recommendations"


def test_unknown_query_does_not_invent_a_capability():
    result = classify_copilot_query(
        CopilotQueryRequest(
            question="Tell me something completely unrelated"
        )
    )

    assert result.intent == CopilotIntent.UNKNOWN
    assert result.suggested_endpoint is None
    assert result.confidence == 0.0
    assert result.evidence_required is True


def test_explanation_query_routes_to_explainability():
    result = classify_copilot_query(
        CopilotQueryRequest(
            question="Why is the environment critical?"
        )
    )

    assert result.intent == CopilotIntent.EXPLANATION
    assert result.suggested_endpoint == "/intelligence/explanations"


def test_review_first_question_routes_to_recommendations():
    result = classify_copilot_query(
        CopilotQueryRequest(
            question="What should we review first?"
        )
    )

    assert result.intent == CopilotIntent.RECOMMENDATION
    assert result.target_capability == "Operational Recommendations"
    assert result.suggested_endpoint == "/intelligence/recommendations"
