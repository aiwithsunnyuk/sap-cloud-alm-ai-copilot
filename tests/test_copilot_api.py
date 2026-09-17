from fastapi.testclient import TestClient

from app.api import app
from app.services.copilot_context_service import clear_context


client = TestClient(app)


def test_copilot_query_deployment_rollback():
    conversation_id = "api-test-deployment"
    clear_context(conversation_id)

    response = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "Why was the deployment rolled back?",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["question"] == "Why was the deployment rolled back?"
    assert body["intent"] == "deployment"
    assert body["grounded"] is True
    assert body["action_required"] is True
    assert body["evidence"]
    assert body["answer"]

    clear_context(conversation_id)


def test_copilot_query_unknown_is_safe():
    conversation_id = "api-test-unknown"
    clear_context(conversation_id)

    response = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "What should I have for lunch today?",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["question"] == "What should I have for lunch today?"
    assert body["intent"] == "unknown"
    assert body["grounded"] is False
    assert body["evidence"] == []
    assert body["answer"]

    clear_context(conversation_id)


def test_copilot_query_preserves_conversation_context():
    conversation_id = "api-test-context"
    clear_context(conversation_id)

    first = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "Why was the deployment rolled back?",
        },
    )

    assert first.status_code == 200

    second = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "What caused it?",
        },
    )

    assert second.status_code == 200

    body = second.json()

    assert body["question"] == "What caused it?"
    assert body["grounded"] is True
    assert body["evidence"]
    assert body["answer"]

    clear_context(conversation_id)


def test_copilot_follow_up_resolves_incident():
    conversation_id = "api-test-follow-up"
    clear_context(conversation_id)

    first = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "Why was the deployment rolled back?",
        },
    )

    assert first.status_code == 200

    second = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "What incident caused it?",
        },
    )

    assert second.status_code == 200

    body = second.json()

    assert body["question"] == "What incident caused it?"
    assert body["intent"] == "incident"
    assert body["grounded"] is True
    assert "INC-003" in body["answer"]
    assert any("INC-003" in item for item in body["evidence"])
    assert body["source_capability"] == "Incident Intelligence"

    clear_context(conversation_id)


def test_copilot_context_retains_evidence_across_turns():
    from app.services.copilot_context_service import (
        get_conversation_evidence,
    )

    conversation_id = "api-test-evidence-continuity"
    clear_context(conversation_id)

    first = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "Why was the deployment rolled back?",
        },
    )

    assert first.status_code == 200

    second = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "What incident caused it?",
        },
    )

    assert second.status_code == 200

    evidence = get_conversation_evidence(
        conversation_id
    )

    assert evidence
    assert any("INC-003" in item for item in evidence)

    clear_context(conversation_id)


def test_copilot_response_preserves_prior_evidence():
    from app.services.copilot_context_service import (
        get_conversation_evidence,
    )

    conversation_id = "api-test-evidence-response"
    clear_context(conversation_id)

    first = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "Why was the deployment rolled back?",
        },
    )

    assert first.status_code == 200

    first_body = first.json()
    first_evidence = first_body["evidence"]

    assert first_evidence
    assert "Failed validations: 1" in first_evidence

    second = client.post(
        "/copilot/query",
        json={
            "conversation_id": conversation_id,
            "question": "What incident caused it?",
        },
    )

    assert second.status_code == 200

    second_body = second.json()
    second_evidence = second_body["evidence"]

    assert "Failed validations: 1" in second_evidence
    assert any("INC-003" in item for item in second_evidence)

    stored_evidence = get_conversation_evidence(
        conversation_id,
    )

    assert stored_evidence == second_evidence

    clear_context(conversation_id)
