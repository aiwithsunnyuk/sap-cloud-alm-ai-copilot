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
