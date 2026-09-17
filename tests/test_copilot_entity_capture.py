from app.services.copilot_entity_capture import capture_entity_context


def test_capture_explicit_deployment():
    context = capture_entity_context(
        question="Show me DEP-001",
        answer="Deployment details.",
        evidence=[],
    )

    assert context is not None
    assert context.primary is not None
    assert context.primary.entity_type == "deployment"
    assert context.primary.entity_id == "DEP-001"


def test_capture_deployment_from_grounded_response():
    context = capture_entity_context(
        question="Why was the deployment rolled back?",
        answer="DEP-001 was rolled back after validation failed.",
        evidence=["Deployment DEP-001", "REL-001"],
    )

    assert context is not None
    assert context.primary is not None
    assert context.primary.entity_type == "deployment"
    assert context.primary.entity_id == "DEP-001"


def test_capture_incident():
    context = capture_entity_context(
        question="Tell me about INC-003",
        answer="INC-003 remains open.",
        evidence=[],
    )

    assert context is not None
    assert context.primary.entity_type == "incident"
    assert context.primary.entity_id == "INC-003"


def test_unknown_entity_is_not_captured():
    context = capture_entity_context(
        question="Tell me about DEP-999",
        answer="No matching deployment exists.",
        evidence=[],
    )

    assert context is None
