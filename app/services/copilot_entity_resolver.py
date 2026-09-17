import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from app.models.copilot_entity_context import (
    CopilotEntityContext,
    CopilotEntityReference,
)


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


_ENTITY_FILES = {
    "deployment": "deployments.json",
    "release": "releases.json",
    "change": "changes.json",
    "problem": "problems.json",
    "incident": "incidents.json",
}


_ID_FIELDS = {
    "deployment": "deployment_id",
    "release": "release_id",
    "change": "change_id",
    "problem": "problem_id",
    "incident": "incident_id",
}


def _load_records(entity_type: str) -> List[dict]:
    filename = _ENTITY_FILES[entity_type]
    path = DATA_DIR / filename

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("items", "data", entity_type + "s"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

    raise ValueError(f"Unsupported data format in {path}")


def _find_record(
    entity_type: str,
    entity_id: str,
) -> Optional[dict]:
    id_field = _ID_FIELDS[entity_type]

    for record in _load_records(entity_type):
        if record.get(id_field) == entity_id:
            return record

    return None


def _reference(
    entity_type: str,
    entity_id: str,
) -> Optional[CopilotEntityReference]:
    record = _find_record(entity_type, entity_id)

    if record is None:
        return None

    id_field = _ID_FIELDS[entity_type]

    title = (
        record.get("title")
        or record.get("name")
        or record.get("description")
        or entity_id
    )

    return CopilotEntityReference(
        entity_type=entity_type,
        entity_id=record[id_field],
        display_name=str(title),
    )


def _append_unique(
    values: List[CopilotEntityReference],
    reference: Optional[CopilotEntityReference],
) -> None:
    if reference is None:
        return

    if not any(
        item.entity_type == reference.entity_type
        and item.entity_id == reference.entity_id
        for item in values
    ):
        values.append(reference)


def build_entity_context(
    entity_type: str,
    entity_id: str,
) -> CopilotEntityContext:
    primary = _reference(entity_type, entity_id)

    if primary is None:
        return CopilotEntityContext()

    related: List[CopilotEntityReference] = []
    relationship_path = [f"{entity_type}:{entity_id}"]

    record = _find_record(entity_type, entity_id)
    assert record is not None

    attributes: Dict[str, str] = {}

    for field in (
        "status",
        "severity",
        "priority",
        "environment",
        "validation_status",
        "rollback_status",
    ):
        value = record.get(field)
        if value is not None:
            attributes[field] = str(value)

    def add_link(
        target_type: str,
        target_id: Optional[str],
        label: str,
    ) -> None:
        if not target_id:
            return

        target = _reference(target_type, target_id)

        if target is not None:
            _append_unique(related, target)
            relationship_path.append(
                f"{label}:{target_type}:{target_id}"
            )

    # Deployment → Release / Change
    if entity_type == "deployment":
        add_link(
            "release",
            record.get("release_id"),
            "release",
        )
        add_link(
            "change",
            record.get("change_id"),
            "change",
        )

    # Release → Change
    elif entity_type == "release":
        add_link(
            "change",
            record.get("change_id"),
            "change",
        )

    # Change → Problem / Incident
    elif entity_type == "change":
        add_link(
            "problem",
            record.get("problem_id"),
            "problem",
        )
        add_link(
            "incident",
            record.get("incident_id"),
            "incident",
        )

    # Problem → related incidents
    elif entity_type == "problem":
        for incident_id in record.get(
            "related_incident_ids",
            [],
        ):
            add_link(
                "incident",
                incident_id,
                "related_incident",
            )

    return CopilotEntityContext(
        primary=primary,
        related_entities=related,
        relationship_path=relationship_path,
        attributes=attributes,
    )


def resolve_entity(
    entity_type: str,
    entity_id: str,
) -> Optional[CopilotEntityContext]:
    if entity_type not in _ENTITY_FILES:
        return None

    return build_entity_context(
        entity_type,
        entity_id,
    )


def find_entity_by_id(
    entity_id: str,
) -> Optional[Tuple[str, CopilotEntityContext]]:
    for entity_type in _ENTITY_FILES:
        if _find_record(entity_type, entity_id) is not None:
            return entity_type, build_entity_context(
                entity_type,
                entity_id,
            )

    return None


def find_related_entity_ids(
    context: CopilotEntityContext,
    entity_type: str,
) -> List[str]:
    return [
        reference.entity_id
        for reference in context.related_entities
        if reference.entity_type == entity_type
    ]
