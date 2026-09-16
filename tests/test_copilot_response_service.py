from app.models.copilot import CopilotIntent, CopilotQueryRequest
from app.services.copilot_response_service import generate_copilot_response


def test_project_health_response_is_grounded():
    result = generate_copilot_response(
        CopilotQueryRequest(
            question="What is the current project status?"
        )
    )

    assert result.intent == CopilotIntent.PROJECT_HEALTH
    assert result.grounded is True
    assert result.evidence
    assert result.source_endpoint == "/operations/control-tower"
    assert result.trace[0] == "Intent Router"


def test_deployment_response_contains_rollback_evidence():
    result = generate_copilot_response(
        CopilotQueryRequest(
            question="Why was the deployment rolled back?"
        )
    )

    assert result.intent == CopilotIntent.DEPLOYMENT
    assert result.grounded is True
    assert result.evidence
    assert "Deployment Intelligence" == result.source_capability


def test_recommendation_response_requires_approval_boundary():
    result = generate_copilot_response(
        CopilotQueryRequest(
            question="What needs attention first?"
        )
    )

    assert result.intent == CopilotIntent.RECOMMENDATION
    assert result.grounded is True
    assert result.evidence
    assert result.approval_required is True


def test_unknown_response_does_not_invent_answer():
    result = generate_copilot_response(
        CopilotQueryRequest(
            question="Tell me something unrelated to ALM"
        )
    )

    assert result.intent == CopilotIntent.UNKNOWN
    assert result.grounded is False
    assert result.evidence == []
    assert result.source_endpoint is None


def test_correlation_response_contains_trace():
    result = generate_copilot_response(
        CopilotQueryRequest(
            question="Show me the causal chain"
        )
    )

    assert result.intent == CopilotIntent.CORRELATION
    assert result.grounded is True
    assert result.evidence
    assert len(result.trace) >= 2
