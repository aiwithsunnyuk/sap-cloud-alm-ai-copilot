from typing import Optional

from app.models.copilot import CopilotIntent
from app.models.copilot_skill import CopilotSkillInvocation
from app.models.copilot_governance import CopilotActionClass
from app.services.copilot_capability_registry import get_capability


def build_skill_invocation(
    intent: CopilotIntent,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> Optional[CopilotSkillInvocation]:
    capability = get_capability(intent)

    if capability is None:
        return None

    action_class = (
        CopilotActionClass.READ_ONLY
        if capability.read_only
        else (
            CopilotActionClass.ACTION
            if capability.approval_required
            else CopilotActionClass.READ_ONLY
        )
    )

    return CopilotSkillInvocation(
        intent=intent,
        capability_name=capability.name,
        endpoint=capability.endpoint,
        read_only=capability.read_only,
        approval_required=capability.approval_required,
        action_class=action_class,
        entity_type=entity_type,
        entity_id=entity_id,
    )
