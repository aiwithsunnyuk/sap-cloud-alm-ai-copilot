from typing import Dict, Optional

from app.models.copilot_context import (
    CopilotContextTurn,
    CopilotConversationContext,
)


_MAX_TURNS = 10

_contexts: Dict[str, CopilotConversationContext] = {}


def get_or_create_context(
    conversation_id: str,
) -> CopilotConversationContext:
    if conversation_id not in _contexts:
        _contexts[conversation_id] = CopilotConversationContext(
            conversation_id=conversation_id
        )

    return _contexts[conversation_id]


def add_turn(
    conversation_id: str,
    turn: CopilotContextTurn,
) -> CopilotConversationContext:
    context = get_or_create_context(conversation_id)

    context.turns.append(turn)

    if len(context.turns) > _MAX_TURNS:
        context.turns = context.turns[-_MAX_TURNS:]

    return context


def get_latest_turn(
    conversation_id: str,
) -> Optional[CopilotContextTurn]:
    return get_or_create_context(conversation_id).latest_turn


def clear_context(conversation_id: str) -> None:
    _contexts.pop(conversation_id, None)


def contextualize_question(
    question: str,
    conversation_id: str,
) -> str:
    """
    Safely enrich an underspecified follow-up with the previous turn.

    The original question is always preserved. We only append context
    when the current question contains an obvious contextual reference.
    """
    latest = get_latest_turn(conversation_id)

    if latest is None:
        return question

    normalized = question.lower()

    contextual_terms = (
        "it",
        "that",
        "this",
        "they",
        "them",
        "what caused",
        "why did",
        "what happened",
        "what should we",
        "what should i",
    )

    if any(term in normalized for term in contextual_terms):
        return (
            f"{question}\n"
            f"Previous Copilot context: "
            f"{latest.intent} discussion. "
            f"Previous answer: {latest.answer}"
        )

    return question
