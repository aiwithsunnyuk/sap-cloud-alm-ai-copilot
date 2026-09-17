from app.models.copilot_context import CopilotContextTurn
from app.services.copilot_context_service import (
    add_turn,
    clear_context,
    contextualize_question,
    get_latest_turn,
)


def test_conversation_context_stores_latest_turn():
    conversation_id = "test-context-001"
    clear_context(conversation_id)

    add_turn(
        conversation_id,
        CopilotContextTurn(
            question="Why was the deployment rolled back?",
            intent="deployment",
            answer="The deployment was rolled back after validation failed.",
            source_capability="Deployment Intelligence",
            grounded=True,
        ),
    )

    latest = get_latest_turn(conversation_id)

    assert latest is not None
    assert latest.intent == "deployment"
    assert latest.grounded is True

    clear_context(conversation_id)


def test_contextualize_follow_up():
    conversation_id = "test-context-002"
    clear_context(conversation_id)

    add_turn(
        conversation_id,
        CopilotContextTurn(
            question="Why was the deployment rolled back?",
            intent="deployment",
            answer="Validation failed and rollback was completed.",
            source_capability="Deployment Intelligence",
            grounded=True,
        ),
    )

    enriched = contextualize_question(
        "What caused it?",
        conversation_id,
    )

    assert "What caused it?" in enriched
    assert "deployment discussion" in enriched
    assert "Validation failed" in enriched

    clear_context(conversation_id)


def test_conversation_context_stores_entity_context():
    from app.models.copilot_entity_context import (
        CopilotEntityContext,
        CopilotEntityReference,
    )
    from app.services.copilot_context_service import (
        add_entity_to_latest_turn,
        get_latest_entity_context,
    )

    conversation_id = "test-entity-context-001"
    clear_context(conversation_id)

    add_turn(
        conversation_id,
        CopilotContextTurn(
            question="Why was the deployment rolled back?",
            intent="deployment",
            answer="Validation failed.",
            grounded=True,
        ),
    )

    entity_context = CopilotEntityContext(
        primary=CopilotEntityReference(
            entity_type="deployment",
            entity_id="DEP-001",
            display_name="DEP-001",
        ),
    )

    add_entity_to_latest_turn(
        conversation_id,
        entity_context,
    )

    latest = get_latest_entity_context(
        conversation_id,
    )

    assert latest is not None
    assert latest.primary is not None
    assert latest.primary.entity_type == "deployment"
    assert latest.primary.entity_id == "DEP-001"

    clear_context(conversation_id)
