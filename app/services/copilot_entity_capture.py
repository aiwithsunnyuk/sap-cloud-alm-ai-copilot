import re
from typing import List, Optional, Tuple

from app.models.copilot_entity_context import CopilotEntityContext
from app.services.copilot_entity_resolver import resolve_entity


_ENTITY_PATTERNS = (
    ("deployment", re.compile(r"\bDEP-\d+\b", re.IGNORECASE)),
    ("release", re.compile(r"\bREL-\d+\b", re.IGNORECASE)),
    ("change", re.compile(r"\bCHG-\d+\b", re.IGNORECASE)),
    ("problem", re.compile(r"\bPRB-\d+\b", re.IGNORECASE)),
    ("incident", re.compile(r"\bINC-\d+\b", re.IGNORECASE)),
)


def _collect_entity_ids(text: str) -> List[Tuple[str, str]]:
    matches: List[Tuple[str, str]] = []

    for entity_type, pattern in _ENTITY_PATTERNS:
        for match in pattern.findall(text):
            item = (entity_type, match.upper())
            if item not in matches:
                matches.append(item)

    return matches


def capture_entity_context(
    question: str,
    answer: str,
    evidence: object,
) -> Optional[CopilotEntityContext]:
    """
    Capture the first concrete operational entity referenced by the
    user's question or by the grounded Copilot response.

    Question matches take precedence because they represent explicit
    user references. Response/evidence matches are used when the user
    asks conceptually, such as "Why was the deployment rolled back?"
    """
    evidence_text = str(evidence)

    matches = (
        _collect_entity_ids(question)
        + _collect_entity_ids(answer)
        + _collect_entity_ids(evidence_text)
    )

    seen = set()

    for entity_type, entity_id in matches:
        key = (entity_type, entity_id)

        if key in seen:
            continue

        seen.add(key)

        context = resolve_entity(
            entity_type,
            entity_id,
        )

        if context is not None and context.primary is not None:
            return context

    return None
