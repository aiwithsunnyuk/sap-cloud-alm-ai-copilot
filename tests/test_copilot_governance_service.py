from app.models.copilot_governance import CopilotActionClass
from app.services.copilot_governance_service import evaluate_governance


def test_read_only_is_allowed():
    decision = evaluate_governance(
        CopilotActionClass.READ_ONLY
    )

    assert decision.allowed is True
    assert decision.approval_required is False


def test_action_requires_approval():
    decision = evaluate_governance(
        CopilotActionClass.ACTION
    )

    assert decision.allowed is False
    assert decision.approval_required is True


def test_high_risk_action_requires_approval():
    decision = evaluate_governance(
        CopilotActionClass.HIGH_RISK_ACTION
    )

    assert decision.allowed is False
    assert decision.approval_required is True
