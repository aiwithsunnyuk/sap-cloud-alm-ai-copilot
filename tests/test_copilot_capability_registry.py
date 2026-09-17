from app.models.copilot import CopilotIntent
from app.services.copilot_capability_registry import (
    get_all_capabilities,
    get_capability,
    get_capability_by_name,
)


def test_all_operational_intents_have_capabilities():
    capabilities = get_all_capabilities()

    intents = {capability.intent for capability in capabilities}

    expected = {
        CopilotIntent.PROJECT_HEALTH,
        CopilotIntent.MONITORING,
        CopilotIntent.INCIDENT,
        CopilotIntent.PROBLEM,
        CopilotIntent.CHANGE,
        CopilotIntent.RELEASE,
        CopilotIntent.DEPLOYMENT,
        CopilotIntent.CORRELATION,
        CopilotIntent.EXPLANATION,
        CopilotIntent.RECOMMENDATION,
        CopilotIntent.DECISION_BRIEF,
    }

    assert intents == expected
    assert len(capabilities) == 11


def test_deployment_capability():
    capability = get_capability(
        CopilotIntent.DEPLOYMENT
    )

    assert capability is not None
    assert capability.name == "Deployment Intelligence"
    assert capability.endpoint == "/deployments/summary"
    assert capability.read_only is True
    assert capability.approval_required is False
    assert "deployment" in capability.supported_entity_types


def test_capability_lookup_by_name():
    capability = get_capability_by_name(
        "incident intelligence"
    )

    assert capability is not None
    assert capability.intent == CopilotIntent.INCIDENT


def test_unknown_capability_returns_none():
    assert get_capability_by_name(
        "not a real capability"
    ) is None
