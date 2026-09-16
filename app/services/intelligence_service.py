from app.models.intelligence import OperationalInsight, IntelligenceResponse
from app.services.operations_control_tower import (
    calculate_operations_control_tower,
)


def generate_operational_intelligence() -> IntelligenceResponse:
    control_tower = calculate_operations_control_tower()

    insights: list[OperationalInsight] = []

    monitoring = control_tower["monitoring"]
    incidents = control_tower["incidents"]
    problems = control_tower["problems"]
    changes = control_tower["changes"]
    deployments = control_tower["deployments"]

    if monitoring["critical_alerts"] > 0:
        insights.append(
            OperationalInsight(
                insight_id="INT-001",
                severity="Critical",
                category="Monitoring",
                title="Critical operational alerts require attention",
                summary=(
                    f"{monitoring['critical_alerts']} critical active alert(s) "
                    "are contributing to the current operational condition."
                ),
                evidence=[
                    f"Active alerts: {monitoring['active_alerts']}",
                    f"Critical alerts: {monitoring['critical_alerts']}",
                    f"High alerts: {monitoring['high_alerts']}",
                ],
                recommended_action=(
                    "Review the critical alerts and confirm operational impact "
                    "before proceeding with affected activities."
                ),
            )
        )

    if incidents["critical_incidents"] > 0:
        insights.append(
            OperationalInsight(
                insight_id="INT-002",
                severity="Critical",
                category="Incident",
                title="Critical incident is affecting operations",
                summary=(
                    f"{incidents['critical_incidents']} critical incident(s) "
                    "remain within the open incident population."
                ),
                evidence=[
                    f"Open incidents: {incidents['open_incidents']}",
                    f"Critical incidents: {incidents['critical_incidents']}",
                    f"High incidents: {incidents['high_incidents']}",
                ],
                recommended_action=(
                    "Prioritize the critical incident and confirm business "
                    "impact, ownership, and containment status."
                ),
            )
        )

    if problems["unresolved_root_causes"] > 0:
        insights.append(
            OperationalInsight(
                insight_id="INT-003",
                severity="High",
                category="Problem Management",
                title="Unresolved root cause is extending operational risk",
                summary=(
                    f"{problems['unresolved_root_causes']} active problem(s) "
                    "still have unresolved root-cause analysis."
                ),
                evidence=[
                    f"Active problems: {problems['active_problems']}",
                    f"Unresolved root causes: "
                    f"{problems['unresolved_root_causes']}",
                ],
                recommended_action=(
                    "Continue RCA and establish corrective and preventive "
                    "actions before treating the problem as resolved."
                ),
            )
        )

    if changes["pending_approval"] > 0:
        insights.append(
            OperationalInsight(
                insight_id="INT-004",
                severity="High",
                category="Change Governance",
                title="Change approval is a potential delivery blocker",
                summary=(
                    f"{changes['pending_approval']} change(s) are awaiting "
                    "approval."
                ),
                evidence=[
                    f"Active changes: {changes['active_changes']}",
                    f"Pending approvals: {changes['pending_approval']}",
                ],
                recommended_action=(
                    "Review pending change approvals before implementation "
                    "or release progression."
                ),
            )
        )

    if deployments["rolled_back_deployments"] > 0:
        insights.append(
            OperationalInsight(
                insight_id="INT-005",
                severity="High",
                category="Deployment",
                title="Rollback activity indicates deployment risk",
                summary=(
                    f"{deployments['rolled_back_deployments']} deployment(s) "
                    "have been rolled back."
                ),
                evidence=[
                    f"Rolled-back deployments: "
                    f"{deployments['rolled_back_deployments']}",
                    f"Failed validations: {deployments['failed_validations']}",
                ],
                recommended_action=(
                    "Review rollback evidence, failed validation checks, "
                    "and corrective actions before repeating deployment."
                ),
            )
        )

    if deployments["failed_validations"] > 0:
        insights.append(
            OperationalInsight(
                insight_id="INT-006",
                severity="High",
                category="Validation",
                title="Deployment validation failure requires review",
                summary=(
                    f"{deployments['failed_validations']} deployment(s) "
                    "have failed validation."
                ),
                evidence=[
                    f"Failed validations: {deployments['failed_validations']}",
                ],
                recommended_action=(
                    "Review validation evidence and confirm remediation "
                    "before the next deployment attempt."
                ),
            )
        )

    critical_count = sum(
        1 for insight in insights if insight.severity == "Critical"
    )
    high_count = sum(
        1 for insight in insights if insight.severity == "High"
    )

    return IntelligenceResponse(
        overall_status=control_tower["overall_status"],
        total_insights=len(insights),
        critical_insights=critical_count,
        high_insights=high_count,
        insights=insights,
    )
