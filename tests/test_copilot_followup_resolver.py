from app.models.copilot_entity_context import (
    CopilotEntityContext,
    CopilotEntityReference,
)
from app.services.copilot_entity_resolver import resolve_entity
from app.services.copilot_followup_resolver import (
    resolve_follow_up_entity,
)


def test_follow_up_resolves_incident_from_deployment():
    context = resolve_entity(
        "deployment",
        "DEP-001",
    )

    result = resolve_follow_up_entity(
        "What incident caused it?",
        context,
    )

    assert result is not None
    assert result.entity_type == "incident"
    assert result.entity_id == "INC-003"


def test_follow_up_resolves_change_from_deployment():
    context = resolve_entity(
        "deployment",
        "DEP-001",
    )

    result = resolve_follow_up_entity(
        "What change affected it?",
        context,
    )

    assert result is not None
    assert result.entity_type == "change"
    assert result.entity_id == "CHG-001"


def test_follow_up_without_explicit_entity_type_keeps_primary():
    context = resolve_entity(
        "deployment",
        "DEP-001",
    )

    result = resolve_follow_up_entity(
        "What happened to it?",
        context,
    )

    assert result is not None
    assert result.entity_type == "deployment"
    assert result.entity_id == "DEP-001"


def test_non_follow_up_question_is_not_forced_into_context():
    context = resolve_entity(
        "deployment",
        "DEP-001",
    )

    result = resolve_follow_up_entity(
        "Show me current incidents.",
        context,
    )

    assert result is None


def test_empty_context_returns_none():
    result = resolve_follow_up_entity(
        "What incident caused it?",
        None,
    )

    assert result is None
