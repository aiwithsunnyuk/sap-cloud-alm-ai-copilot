from app.models.copilot_session import CopilotSessionSummary
from app.services.copilot_context_service import (
    get_conversation_evidence,
    get_or_create_context,
)


def get_session_summary(
    conversation_id: str,
) -> CopilotSessionSummary:
    context = get_or_create_context(conversation_id)

    latest = context.latest_turn

    current_entity_type = None
    current_entity_id = None
    related_entities: list[str] = []

    if latest is not None and latest.entity_context is not None:
        entity_context = latest.entity_context

        if entity_context.primary is not None:
            current_entity_type = entity_context.primary.entity_type
            current_entity_id = entity_context.primary.entity_id

        related_entities = [
            f"{item.entity_type}:{item.entity_id}"
            for item in entity_context.related_entities
        ]

    grounded_turn_count = sum(
        1
        for turn in context.turns
        if turn.grounded
    )

    return CopilotSessionSummary(
        conversation_id=conversation_id,
        turn_count=len(context.turns),
        latest_intent=(
            latest.intent
            if latest is not None
            else None
        ),
        current_entity_type=current_entity_type,
        current_entity_id=current_entity_id,
        related_entities=related_entities,
        evidence_count=len(
            get_conversation_evidence(conversation_id)
        ),
        grounded_turn_count=grounded_turn_count,
    )
