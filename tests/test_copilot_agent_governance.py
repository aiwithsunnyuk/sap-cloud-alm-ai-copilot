from app.services.copilot_agent_governance import (
    evaluate_agent_governance,
)


def test_read_only_agent_is_allowed_to_query():
    result = evaluate_agent_governance(
        "deployment-investigator",
        requested_action=False,
    )

    assert result.allowed is True
    assert result.read_only is True
    assert result.approval_required is False
    assert "Read-Only Access Allowed" in result.trace


def test_read_only_agent_cannot_execute_action():
    result = evaluate_agent_governance(
        "deployment-investigator",
        requested_action=True,
    )

    assert result.allowed is False
    assert result.read_only is True
    assert result.approval_required is True
    assert "Blocked: Read-Only Agent" in result.trace


def test_unknown_agent_is_blocked():
    result = evaluate_agent_governance(
        "not-a-real-agent",
    )

    assert result.allowed is False
    assert result.agent_name == "Unknown Agent"
    assert "Blocked: Unknown Agent" in result.trace


def test_governance_can_allow_registered_non_read_only_agent():
    from app.models.copilot import CopilotIntent
    from app.models.copilot_agent import CopilotAgent
    from app.services import copilot_agent_governance

    original = copilot_agent_governance.get_agent

    fake_agent = CopilotAgent(
        agent_id="test-action-agent",
        name="Test Action Agent",
        description="Governance test agent",
        intents=[CopilotIntent.DEPLOYMENT],
        skills=[],
        read_only=False,
        approval_required=False,
    )

    copilot_agent_governance.get_agent = (
        lambda agent_id: (
            fake_agent
            if agent_id == "test-action-agent"
            else original(agent_id)
        )
    )

    try:
        result = evaluate_agent_governance(
            "test-action-agent",
            requested_action=True,
        )

        assert result.allowed is True
        assert result.read_only is False
        assert result.approval_required is False
        assert "Action Allowed" in result.trace
    finally:
        copilot_agent_governance.get_agent = original


def test_non_read_only_approved_agent_can_execute():
    from app.models.copilot import CopilotIntent
    from app.models.copilot_agent import CopilotAgent
    from app.services import copilot_agent_governance

    original = copilot_agent_governance.get_agent

    fake_agent = CopilotAgent(
        agent_id="approval-agent",
        name="Approval Agent",
        description="Approval governance test agent",
        intents=[CopilotIntent.DEPLOYMENT],
        skills=[],
        read_only=False,
        approval_required=True,
    )

    copilot_agent_governance.get_agent = (
        lambda agent_id: (
            fake_agent
            if agent_id == "approval-agent"
            else original(agent_id)
        )
    )

    try:
        blocked = evaluate_agent_governance(
            "approval-agent",
            requested_action=True,
            approved=False,
        )

        assert blocked.allowed is False
        assert blocked.approval_required is True

        allowed = evaluate_agent_governance(
            "approval-agent",
            requested_action=True,
            approved=True,
        )

        assert allowed.allowed is True
        assert allowed.approval_required is True
        assert "Action Allowed" in allowed.trace
    finally:
        copilot_agent_governance.get_agent = original
