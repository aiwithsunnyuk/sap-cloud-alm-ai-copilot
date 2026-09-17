import re
from typing import List, Optional, Tuple

from app.models.copilot_entity_context import CopilotEntityContext
from app.services.copilot_entity_resolver import resolve_entity
from app.services.deployment_service import get_deployments
from app.models.deployments import DeploymentStatus


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


def _capture_implicit_deployment(
    question: str,
    answer: str,
) -> Optional[CopilotEntityContext]:
    combined = f"{question} {answer}".lower()

    # The current operational scenario contains a single rolled-back
    # deployment. Resolve it when the user is explicitly asking about
    # a rollback/deployment failure without naming its ID.
    rollback_terms = (
        "rolled back",
        "rollback",
        "failed validation",
        "deployment failure",
    )

    if "deployment" not in combined:
        return None

    if not any(term in combined for term in rollback_terms):
        return None

    rolled_back = [
        deployment
        for deployment in get_deployments()
        if deployment.deployment_status
        == DeploymentStatus.ROLLED_BACK
    ]

    if len(rolled_back) != 1:
        return None

    return resolve_entity(
        "deployment",
        rolled_back[0].deployment_id,
    )


def capture_entity_context(
    question: str,
    answer: str,
    evidence: object,
) -> Optional[CopilotEntityContext]:
    """
    Capture a concrete operational entity from explicit identifiers.

    When a grounded response does not expose an identifier directly,
    use a narrow deterministic inference for the current operational
    scenario, such as a uniquely rolled-back deployment.
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

    return _capture_implicit_deployment(
        question,
        answer,
    )
