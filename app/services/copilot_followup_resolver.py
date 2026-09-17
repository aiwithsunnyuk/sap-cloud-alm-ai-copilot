import re
from typing import Optional

from app.models.copilot_context import CopilotContextTurn
from app.models.copilot_entity_context import (
    CopilotEntityContext,
    CopilotEntityReference,
)
from app.services.copilot_entity_resolver import resolve_entity


_REFERENCE_TERMS = (
    "it",
    "that",
    "this",
    "that one",
    "this one",
)


_ENTITY_TERMS = {
    "deployment": ("deployment", "deployment"),
    "release": ("release", "release"),
    "change": ("change", "change request"),
    "problem": ("problem", "problem record"),
    "incident": ("incident", "incident"),
}


def _requested_entity_type(question: str) -> Optional[str]:
    normalized = question.lower()

    for entity_type, terms in _ENTITY_TERMS.items():
        if any(term in normalized for term in terms):
            return entity_type

    return None


def _has_reference_term(question: str) -> bool:
    normalized = question.lower()

    return any(
        re.search(
            rf"\b{re.escape(term)}\b",
            normalized,
        )
        for term in _REFERENCE_TERMS
    )


def _find_related_entity(
    context: CopilotEntityContext,
    entity_type: str,
) -> Optional[CopilotEntityReference]:
    if context.primary is None:
        return None

    # Direct relationship.
    for reference in context.related_entities:
        if reference.entity_type == entity_type:
            return reference

    # Traverse the relationship graph from the known entities.
    pending = list(context.related_entities)
    visited = set()

    while pending:
        reference = pending.pop(0)
        key = (reference.entity_type, reference.entity_id)

        if key in visited:
            continue

        visited.add(key)

        if reference.entity_type == entity_type:
            return reference

        nested = resolve_entity(
            reference.entity_type,
            reference.entity_id,
        )

        if nested is None:
            continue

        for related in nested.related_entities:
            related_key = (
                related.entity_type,
                related.entity_id,
            )

            if related_key not in visited:
                pending.append(related)

    return None


def resolve_follow_up_entity(
    question: str,
    previous_context: Optional[CopilotEntityContext],
) -> Optional[CopilotEntityReference]:
    """
    Resolve a follow-up question against the previous operational entity.

    Examples:
      "What incident caused it?"
        deployment:DEP-001 -> incident:INC-003

      "What change affected it?"
        deployment:DEP-001 -> change:CHG-001
    """
    if previous_context is None:
        return None

    if previous_context.primary is None:
        return None

    if not _has_reference_term(question):
        return None

    requested_type = _requested_entity_type(question)

    if requested_type is not None:
        return _find_related_entity(
            previous_context,
            requested_type,
        )

    return previous_context.primary
