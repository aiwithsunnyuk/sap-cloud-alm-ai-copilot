from app.models.copilot import CopilotIntent
from app.models.copilot_multi_agent import (
    CopilotAgentOrchestrationInput,
    CopilotMultiAgentDecisionRequest,
)
from app.models.copilot_decision import CopilotDecisionStatus
from app.services.copilot_decision_assessment import (
    assess_multi_agent_decision,
)
from app.services.copilot_orchestrator import orchestrate_skill


def test_real_multi_agent_decision_assessment():
    deployment_result = orchestrate_skill(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    incident_result = orchestrate_skill(
        CopilotIntent.INCIDENT,
        entity_type="incident",
        entity_id="INC-003",
    )

    release_result = orchestrate_skill(
        CopilotIntent.RELEASE,
        entity_type="release",
        entity_id="REL-001",
    )

    assert deployment_result is not None
    assert incident_result is not None
    assert release_result is not None

    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="What should we review before proceeding with the deployment?",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=deployment_result,
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="incident-investigator",
                    orchestration=incident_result,
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="release-governance",
                    orchestration=release_result,
                ),
            ],
        )
    )

    assert result.auditable is True

    assert result.decision.status == CopilotDecisionStatus.SUCCESS

    assert result.decision.contributing_agents == [
        "deployment-investigator",
        "incident-investigator",
        "release-governance",
    ]

    assert len(result.decision.evidence) > 0

    assert result.confidence.score >= 80
    assert result.confidence.level.value == "high"

    assert result.trace == [
        "Multi-Agent Decision Orchestration",
        "Decision Candidate",
        "Decision Confidence",
        "Decision Assessment",
    ]


def test_real_deployment_orchestration_produces_expected_tools():
    result = orchestrate_skill(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    assert result is not None
    assert result.skill_name == "Deployment Investigation"
    assert result.intent == CopilotIntent.DEPLOYMENT
    assert result.status == "success"
    assert result.successful_tools == 3
    assert result.failed_tools == 0
    assert result.blocked_tools == 0

    tool_names = {
        item.tool_name
        for item in result.tool_results
    }

    assert tool_names == {
        "get_deployment_summary",
        "get_operational_correlations",
        "get_operational_recommendations",
    }

    assert "Multi-Tool Orchestrator" in result.trace


def test_real_multi_agent_assessment_preserves_evidence():
    deployment_result = orchestrate_skill(
        CopilotIntent.DEPLOYMENT,
        entity_type="deployment",
        entity_id="DEP-001",
    )

    incident_result = orchestrate_skill(
        CopilotIntent.INCIDENT,
        entity_type="incident",
        entity_id="INC-003",
    )

    result = assess_multi_agent_decision(
        CopilotMultiAgentDecisionRequest(
            question="Investigate deployment impact",
            intent=CopilotIntent.DEPLOYMENT,
            agent_results=[
                CopilotAgentOrchestrationInput(
                    agent_id="deployment-investigator",
                    orchestration=deployment_result,
                ),
                CopilotAgentOrchestrationInput(
                    agent_id="incident-investigator",
                    orchestration=incident_result,
                ),
            ],
        )
    )

    assert result.decision.status == CopilotDecisionStatus.SUCCESS
    assert len(result.decision.evidence) > 0
    assert len(result.decision.contributing_agents) == 2
    assert result.confidence.score >= 80
