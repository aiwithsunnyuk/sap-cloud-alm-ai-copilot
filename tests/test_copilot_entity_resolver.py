from app.services.copilot_entity_resolver import (
    find_entity_by_id,
    find_related_entity_ids,
    resolve_entity,
)


def test_resolve_deployment_chain():
    context = resolve_entity("deployment", "DEP-001")

    assert context is not None
    assert context.primary is not None
    assert context.primary.entity_type == "deployment"
    assert context.primary.entity_id == "DEP-001"

    assert "REL-001" in find_related_entity_ids(
        context,
        "release",
    )
    assert "CHG-001" in find_related_entity_ids(
        context,
        "change",
    )

    assert context.relationship_path[0] == "deployment:DEP-001"


def test_resolve_change_to_incident():
    context = resolve_entity("change", "CHG-001")

    assert context is not None

    assert "PRB-001" in find_related_entity_ids(
        context,
        "problem",
    )

    assert "INC-003" in find_related_entity_ids(
        context,
        "incident",
    )


def test_resolve_problem_related_incidents():
    context = resolve_entity("problem", "PRB-001")

    assert context is not None

    incidents = find_related_entity_ids(
        context,
        "incident",
    )

    assert "INC-001" in incidents
    assert "INC-003" in incidents


def test_find_entity_by_id():
    result = find_entity_by_id("DEP-001")

    assert result is not None

    entity_type, context = result

    assert entity_type == "deployment"
    assert context.primary.entity_id == "DEP-001"


def test_unknown_entity_returns_empty_context():
    context = resolve_entity(
        "deployment",
        "DEP-999",
    )

    assert context is not None
    assert context.primary is None
    assert context.related_entities == []
