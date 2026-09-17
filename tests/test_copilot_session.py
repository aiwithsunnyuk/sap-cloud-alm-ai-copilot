from fastapi.testclient import TestClient

from app.api import app
from app.models.copilot_context import CopilotContextTurn
from app.models.copilot_entity_context import (
    CopilotEntityContext,
    CopilotEntityReference,
)
from app.services.copilot_context_service import (
    add_turn,
    clear_context,
)
from app.services.copilot_session_service import (
    get_session_summary,
)


client = TestClient(app)


def test_session_summary_empty_context():
    conversation_id = "session-empty"
    clear_context(conversation_id)

    summary = get_session_summary(conversation_id)

    assert summary.conversation_id == conversation_id
    assert summary.turn_count == 0
    assert summary.latest_intent is None
    assert summary.current_entity_id is None
    assert summary.evidence_count == 0
    assert summary.grounded_turn_count == 0

    clear_context(conversation_id)


def test_session_summary_tracks_entity_and_evidence():
    conversation_id = "session-summary"
    clear_context(conversation_id)

    add_turn(
        conversation_id,
        CopilotContextTurn(
            question="Why was the deployment rolled back?",
            intent="deployment",
            answer="Validation failed.",
            evidence=[
                "DEP-001",
                "Validation: Failed",
            ],
            grounded=True,
            entity_context=CopilotEntityContext(
                primary=CopilotEntityReference(
                    entity_type="deployment",
                    entity_id="DEP-001",
                    display_name="DEP-001",
                ),
                related_entities=[
                    CopilotEntityReference(
                        entity_type="release",
                        entity_id="REL-001",
                        display_name="REL-001",
                    ),
                    CopilotEntityReference(
                        entity_type="change",
                        entity_id="CHG-001",
                        display_name="CHG-001",
                    ),
                ],
            ),
        ),
    )

    summary = get_session_summary(conversation_id)

    assert summary.turn_count == 1
    assert summary.latest_intent == "deployment"
    assert summary.current_entity_type == "deployment"
    assert summary.current_entity_id == "DEP-001"
    assert "release:REL-001" in summary.related_entities
    assert "change:CHG-001" in summary.related_entities
    assert summary.evidence_count == 2
    assert summary.grounded_turn_count == 1

    clear_context(conversation_id)


def test_session_summary_api():
    conversation_id = "session-api"
    clear_context(conversation_id)

    response = client.get(
        f"/copilot/context/{conversation_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["conversation_id"] == conversation_id
    assert body["turn_count"] == 0
    assert body["current_entity_id"] is None

    clear_context(conversation_id)
