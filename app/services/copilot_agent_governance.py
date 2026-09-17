from app.models.copilot_agent_governance import (
    CopilotAgentGovernance,
)
from app.services.copilot_agent_registry import get_agent


def evaluate_agent_governance(
    agent_id: str,
    *,
    requested_action: bool = False,
    approved: bool = False,
) -> CopilotAgentGovernance:
    trace = [
        "Agent Registry",
        "Agent Governance",
    ]

    agent = get_agent(agent_id)

    if agent is None:
        return CopilotAgentGovernance(
            agent_id=agent_id,
            agent_name="Unknown Agent",
            allowed=False,
            read_only=True,
            approval_required=False,
            reason="Agent is not registered.",
            trace=trace + ["Blocked: Unknown Agent"],
        )

    if not requested_action:
        return CopilotAgentGovernance(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            allowed=True,
            read_only=agent.read_only,
            approval_required=False,
            reason=(
                "Read-only agent activity is permitted "
                "without approval."
            ),
            trace=trace + ["Read-Only Access Allowed"],
        )

    if agent.read_only:
        return CopilotAgentGovernance(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            allowed=False,
            read_only=True,
            approval_required=True,
            reason=(
                "The selected agent is registered as read-only "
                "and cannot execute operational actions."
            ),
            trace=trace + ["Blocked: Read-Only Agent"],
        )

    if agent.approval_required and not approved:
        return CopilotAgentGovernance(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            allowed=False,
            read_only=False,
            approval_required=True,
            reason=(
                "Operational action requires explicit approval."
            ),
            trace=trace + ["Approval Required"],
        )

    return CopilotAgentGovernance(
        agent_id=agent.agent_id,
        agent_name=agent.name,
        allowed=True,
        read_only=False,
        approval_required=agent.approval_required,
        reason=(
            "Operational action passed the registered "
            "agent governance policy."
        ),
        trace=trace + ["Action Allowed"],
    )
