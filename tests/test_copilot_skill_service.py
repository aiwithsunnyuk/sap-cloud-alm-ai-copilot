from app.models.copilot import CopilotIntent
from app.models.copilot_governance import CopilotActionClass
from app.services.copilot_skill_service import (
    build_skill_invocation,
)


def test_build_deployment_skill():
    skill = build_skill_invocation(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    assert skill is not None
    assert skill.intent == CopilotIntent.DEPLOYMENT
    assert skill.capability_name == "Deployment Intelligence"
    assert skill.endpoint == "/deployments/summary"
    assert skill.read_only is True
    assert skill.approval_required is False
    assert skill.entity_type == "deployment"
    assert skill.entity_id == "DEP-001"


def test_build_recommendation_skill():
    skill = build_skill_invocation(
        CopilotIntent.RECOMMENDATION,
    )

    assert skill is not None
    assert skill.capability_name == "Operational Recommendations"
    assert skill.endpoint == "/intelligence/recommendations"
    assert skill.read_only is True


def test_unknown_skill_returns_none():
    skill = build_skill_invocation(
        CopilotIntent.UNKNOWN,
    )

    assert skill is None

def test_read_only_skill_has_read_only_governance():
    skill = build_skill_invocation(
        CopilotIntent.DEPLOYMENT,
    )

    assert skill is not None
    assert skill.action_class == CopilotActionClass.READ_ONLY
    assert skill.approval_required is False

