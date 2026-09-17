from app.models.copilot_governance import (
    CopilotActionClass,
    CopilotGovernanceDecision,
)


def evaluate_governance(
    action_class: CopilotActionClass,
) -> CopilotGovernanceDecision:
    if action_class == CopilotActionClass.READ_ONLY:
        return CopilotGovernanceDecision(
            action_class=action_class,
            allowed=True,
            approval_required=False,
            reason="Read-only operational intelligence is permitted.",
        )

    if action_class == CopilotActionClass.ACTION:
        return CopilotGovernanceDecision(
            action_class=action_class,
            allowed=False,
            approval_required=True,
            reason="Operational actions require explicit human approval.",
        )

    return CopilotGovernanceDecision(
        action_class=action_class,
        allowed=False,
        approval_required=True,
        reason="High-risk actions require explicit governance approval.",
    )
