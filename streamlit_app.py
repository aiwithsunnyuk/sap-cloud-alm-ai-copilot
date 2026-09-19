import os

import requests
import streamlit as st
from fastapi.testclient import TestClient

from app.api import app as fastapi_app


API_BASE_URL = os.getenv("API_BASE_URL", "").strip().rstrip("/")

_local_client = TestClient(fastapi_app)


st.set_page_config(
    page_title="SAP Cloud ALM AI Copilot",
    page_icon="📊",
    layout="wide",
)


def api_get(path: str):
    if API_BASE_URL:
        url = f"{API_BASE_URL}{path}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    response = _local_client.get(path)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict):
    if API_BASE_URL:
        url = f"{API_BASE_URL}{path}"
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    response = _local_client.post(path, json=payload)
    response.raise_for_status()
    return response.json()


def health_color(health: str) -> str:
    return {
        "Green": "🟢",
        "Amber": "🟠",
        "Red": "🔴",
    }.get(health, "⚪")


st.title("SAP Cloud ALM AI Copilot")
st.caption("Delivery Intelligence • Risk • Health • Early Warnings")

# M16.5 SAP Cloud ALM source status
try:
    source_status = api_get("/integration/calm/status")

    st.markdown("### SAP Cloud ALM Data Source")

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric(
            "Data Source",
            source_status.get("data_source", "unknown").title(),
        )

    with s2:
        st.metric(
            "Configured",
            "Yes" if source_status.get("configured") else "No",
        )

    with s3:
        st.metric(
            "Authenticated",
            "Yes" if source_status.get("authenticated") else "No",
        )

    with s4:
        st.metric(
            "Connection",
            source_status.get(
                "connection_status",
                "unknown",
            ).replace("_", " ").title(),
        )

    st.caption(
        source_status.get(
            "message",
            "No source status message available.",
        )
    )

except Exception as exc:
    st.warning(f"Data source status unavailable: {exc}")


st.divider()

try:
    project_data = api_get("/projects")
    risk_data = api_get("/risks/summary")
    workstream_data = api_get("/workstreams/summary")
    early_warning_data = api_get("/api/v1/early-warnings")

except requests.RequestException as exc:
    st.error(
        "Unable to connect to the FastAPI backend. "
        "Make sure the API is running and API_BASE_URL is correct."
    )
    st.code(str(exc))
    st.stop()


# ------------------------------------------------------------------
# Executive KPIs
# ------------------------------------------------------------------

st.subheader("Executive Delivery Overview")

critical = risk_data.get("critical", 0)
high = risk_data.get("high", 0)
medium = risk_data.get("medium", 0)
low = risk_data.get("low", 0)

total_tasks = risk_data.get("total_tasks", 0)
total_warnings = early_warning_data.get("total_warnings", 0)
critical_warnings = early_warning_data.get("critical_warnings", 0)

assessments = risk_data.get("assessments", [])

average_risk = (
    sum(item.get("risk_score", 0) for item in assessments) / len(assessments)
    if assessments
    else 0
)

blocked_tasks = sum(
    1
    for item in assessments
    if item.get("status") == "Blocked"
)

overall_status = early_warning_data.get("overall_status", "Unknown")


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Tasks", total_tasks)

with col2:
    st.metric("Avg Risk Score", f"{average_risk:.1f}")

with col3:
    st.metric("Critical Risks", critical)

with col4:
    st.metric("Blocked Tasks", blocked_tasks)

with col5:
    st.metric("Early Warnings", total_warnings)


st.divider()


# ------------------------------------------------------------------
# Executive status
# ------------------------------------------------------------------

status_col, distribution_col = st.columns([1, 2])

with status_col:
    st.subheader("Overall Delivery Status")

    if overall_status == "Critical":
        st.error("🔴 CRITICAL")
    elif overall_status == "High":
        st.warning("🟠 HIGH")
    elif overall_status == "Healthy":
        st.success("🟢 HEALTHY")
    else:
        st.info(f"⚪ {overall_status}")

    st.write(
        early_warning_data.get(
            "executive_action",
            "No executive action currently available.",
        )
    )

with distribution_col:
    st.subheader("Risk Distribution")

    risk_distribution = {
        "Critical": critical,
        "High": high,
        "Medium": medium,
        "Low": low,
    }

    st.bar_chart(risk_distribution)


st.divider()


# ------------------------------------------------------------------
# Workstream health
# ------------------------------------------------------------------

# ===== M9/M10 OPERATIONS INTELLIGENCE COCKPIT =====

st.divider()

st.markdown(
    """
    <style>
    .oi-hero {
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 1rem;
    }

    .oi-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .oi-subtitle {
        font-size: 0.95rem;
        opacity: 0.75;
    }

    .oi-card {
        padding: 0.9rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.22);
        min-height: 92px;
    }

    .oi-label {
        font-size: 0.78rem;
        opacity: 0.7;
    }

    .oi-value {
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }

    .oi-status {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="oi-hero">
        <div class="oi-title">🧠 SAP Cloud ALM AI Copilot</div>
        <div class="oi-subtitle">
            Operations Intelligence Center · Evidence-driven delivery and
            operational decision support
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

control_tower = api_get("/operations/control-tower") or {}
operational_intelligence = api_get("/intelligence/operational") or {}
correlations = api_get("/intelligence/correlations") or {}
explanations = api_get("/intelligence/explanations") or {}
recommendations = api_get("/intelligence/recommendations") or {}
decision_brief = api_get("/intelligence/decision-brief") or {}

monitoring = control_tower.get("monitoring", {})
incidents = control_tower.get("incidents", {})
problems = control_tower.get("problems", {})
changes = control_tower.get("changes", {})
releases = control_tower.get("releases", {})
deployments = control_tower.get("deployments", {})

overall_status = control_tower.get(
    "overall_status",
    decision_brief.get("overall_status", "Unknown"),
)

metrics = [
    ("Overall Status", overall_status),
    ("Active Alerts", monitoring.get("active_alerts", 0)),
    ("Open Incidents", incidents.get("open_incidents", 0)),
    ("Active Problems", problems.get("active_problems", 0)),
    ("Pending Approvals", changes.get("pending_approval", 0)),
    ("Active Releases", releases.get("active_releases", 0)),
    ("Rolled Back", deployments.get("rolled_back_deployments", 0)),
    ("Failed Validation", deployments.get("failed_validations", 0)),
]

metric_columns = st.columns(4)

for index, (label, value) in enumerate(metrics):
    with metric_columns[index % 4]:
        st.markdown(
            f"""
            <div class="oi-card">
                <div class="oi-label">{label}</div>
                <div class="oi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if index == 3:
        metric_columns = st.columns(4)

st.write("")

tabs = st.tabs([
    "Overview",
    "Intelligence",
    "Correlations",
    "Explainability",
    "Recommendations",
    "Decision Brief",
    "🤖 Copilot",
    "🧭 Decisions",
    "🔐 Governance",
])

# ------------------------------------------------------------------
# Overview
# ------------------------------------------------------------------

with tabs[0]:
    st.subheader("Operations Control Tower")

    overview_col1, overview_col2 = st.columns([1.1, 1])

    with overview_col1:
        st.markdown("**Operational Status**")

        st.info(
            f"Current environment status: **{overall_status}**"
        )

        executive_actions = control_tower.get(
            "executive_actions",
            [],
        )

        if executive_actions:
            st.markdown("**Immediate Review Points**")
            for action in executive_actions:
                st.write(f"• {action}")

    with overview_col2:
        st.markdown("**Affected Scope**")

        affected_components = control_tower.get(
            "affected_components",
            [],
        )

        affected_workstreams = control_tower.get(
            "affected_workstreams",
            [],
        )

        if affected_components:
            st.markdown("**Components**")
            st.write(" · ".join(affected_components))

        if affected_workstreams:
            st.markdown("**Workstreams**")
            st.write(" · ".join(affected_workstreams))

# ------------------------------------------------------------------
# Intelligence
# ------------------------------------------------------------------

with tabs[1]:
    st.subheader("Operational Intelligence")

    insights = operational_intelligence.get("insights", [])

    if not insights:
        st.success("No active intelligence insights.")
    else:
        for insight in insights:
            severity = insight.get("severity", "Unknown")
            title = insight.get("title", "Operational Insight")

            with st.expander(
                f"{severity} · {title}",
                expanded=(severity == "Critical"),
            ):
                st.write(insight.get("summary", ""))

                evidence = insight.get("evidence", [])

                if evidence:
                    st.markdown("**Evidence**")
                    for item in evidence:
                        st.write(f"• {item}")

                action = insight.get("recommended_action")

                if action:
                    st.markdown("**Recommended Action**")
                    st.write(action)

# ------------------------------------------------------------------
# Correlations
# ------------------------------------------------------------------

with tabs[2]:
    st.subheader("Cross-Domain Correlations")

    correlation_items = correlations.get("correlations", [])

    if not correlation_items:
        st.info("No cross-domain correlations available.")
    else:
        for item in correlation_items:
            severity = item.get("severity", "Unknown")
            title = item.get("title", "Operational Correlation")

            with st.expander(
                f"{severity} · {title}",
                expanded=(severity == "Critical"),
            ):
                chain = item.get("causal_chain", [])

                if chain:
                    st.markdown("**Operational Chain**")
                    st.code("  →  ".join(chain))

                summary = item.get("summary")

                if summary:
                    st.write(summary)

                evidence = item.get("evidence", [])

                if evidence:
                    st.markdown("**Evidence Trail**")
                    for entry in evidence:
                        st.write(f"• {entry}")

# ------------------------------------------------------------------
# Explainability
# ------------------------------------------------------------------

with tabs[3]:
    st.subheader("Explainability")

    explanation_items = explanations.get("explanations", [])

    if not explanation_items:
        st.info("No explanations available.")
    else:
        for explanation in explanation_items:
            severity = explanation.get("severity", "Unknown")
            title = explanation.get(
                "title",
                "Operational Explanation",
            )

            with st.expander(
                f"{severity} · {title}",
                expanded=(severity == "Critical"),
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**What happened?**")
                    st.write(
                        explanation.get("what_happened", "")
                    )

                with col2:
                    st.markdown("**Why does it matter?**")
                    st.write(
                        explanation.get("why_it_matters", "")
                    )

                st.markdown("**Operational Impact**")
                st.write(
                    explanation.get("operational_impact", "")
                )

                st.markdown("**Evidence**")
                for evidence_item in explanation.get(
                    "evidence",
                    [],
                ):
                    st.write(f"• {evidence_item}")

                st.markdown("**Recommended Review**")
                st.write(
                    explanation.get("recommended_review", "")
                )

# ------------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------------

with tabs[4]:
    st.subheader("Prioritized Recommendations")

    recommendation_items = recommendations.get(
        "recommendations",
        [],
    )

    if not recommendation_items:
        st.success("No operational recommendations.")
    else:
        priority_summary = st.columns(3)

        with priority_summary[0]:
            st.metric(
                "P1",
                recommendations.get(
                    "p1_recommendations",
                    0,
                ),
            )

        with priority_summary[1]:
            st.metric(
                "P2",
                recommendations.get(
                    "p2_recommendations",
                    0,
                ),
            )

        with priority_summary[2]:
            st.metric(
                "Total",
                recommendations.get(
                    "total_recommendations",
                    0,
                ),
            )

        for item in recommendation_items:
            priority = item.get("priority", "P4")
            score = item.get("priority_score", 0)
            title = item.get("title", "Recommendation")

            with st.expander(
                f"{priority} · Score {score} · {title}",
                expanded=(priority == "P1"),
            ):
                st.markdown("**Action**")
                st.write(item.get("action", ""))

                st.markdown("**Rationale**")
                st.write(item.get("rationale", ""))

                evidence = item.get("evidence", [])

                if evidence:
                    st.markdown("**Evidence**")
                    for evidence_item in evidence:
                        st.write(f"• {evidence_item}")

                st.caption(
                    f"Source explanation: "
                    f"{item.get('source_explanation', 'N/A')}"
                )

# ------------------------------------------------------------------
# Decision Brief
# ------------------------------------------------------------------

with tabs[5]:
    st.subheader("Executive Decision Brief")

    summary = decision_brief.get("executive_summary")

    if summary:
        st.info(summary)

    brief_col1, brief_col2 = st.columns(2)

    with brief_col1:
        st.metric(
            "Total Risks",
            decision_brief.get("total_risks", 0),
        )

    with brief_col2:
        st.metric(
            "Priority Actions",
            decision_brief.get(
                "priority_actions_count",
                0,
            ),
        )

    st.markdown("**Top Risks**")

    for risk in decision_brief.get("top_risks", []):
        st.write(f"• {risk}")

    st.markdown("**Decision Points**")

    for point in decision_brief.get("decision_points", []):
        st.write(f"• {point}")

    evidence = decision_brief.get("evidence", [])

    if evidence:
        st.markdown("**Evidence Snapshot**")
        for item in evidence:
            st.write(f"• {item}")

st.caption(
    "Decision-support only · Synthetic demo data · "
    "No autonomous operational actions are executed"
)

st.subheader("Workstream Health")

workstreams = workstream_data.get("workstreams", [])

if not workstreams:
    st.info("No workstream data available.")
else:
    columns = st.columns(min(len(workstreams), 3))

    for index, workstream in enumerate(workstreams):
        column = columns[index % len(columns)]

        health = workstream.get("overall_health", "Unknown")
        highest_risk = workstream.get("highest_risk_task") or {}

        with column:
            st.markdown(
                f"### {health_color(health)} "
                f"{workstream.get('workstream_id', 'Unknown')}"
            )

            st.write(
                f"**Tasks:** {workstream.get('total_tasks', 0)}  \n"
                f"**Risk score:** "
                f"{workstream.get('average_risk_score', 0):.1f}  \n"
                f"**Critical:** {workstream.get('critical', 0)}  \n"
                f"**High:** {workstream.get('high', 0)}  \n"
                f"**Blocked:** {workstream.get('blocked_tasks', 0)}"
            )

            if highest_risk:
                st.caption(
                    "Highest risk: "
                    f"{highest_risk.get('task_id', 'Unknown')} "
                    f"• {highest_risk.get('risk_score', 0)} "
                    f"• {highest_risk.get('risk_level', 'Unknown')}"
                )


st.divider()


# ------------------------------------------------------------------
# Early warnings
# ------------------------------------------------------------------

st.subheader("🚨 Early Warning Cockpit")

warnings = early_warning_data.get("warnings", [])

if critical_warnings:
    st.error(
        f"{critical_warnings} critical warning(s) require immediate attention."
    )

if not warnings:
    st.success("No active early warnings.")
else:
    for warning in warnings:
        severity = warning.get("severity", "Unknown")
        title = warning.get("title") or warning.get("warning_type")

        if severity == "Critical":
            st.error(f"🔴 {title}")
        elif severity == "High":
            st.warning(f"🟠 {title}")
        else:
            st.info(f"🔵 {title}")

        st.write(warning.get("message", ""))

        action = warning.get("recommended_action")
        if action:
            st.caption(f"Recommended action: {action}")


st.divider()


# ------------------------------------------------------------------
# Task risk explorer
# ------------------------------------------------------------------

# ------------------------------------------------------------
# Historical risk intelligence
# ------------------------------------------------------------

st.divider()

st.subheader("📈 Historical Risk Intelligence")

if assessments:
    historical_task_names = [
        f"{item.get('task_id', '')} | {item.get('task_name', '')}"
        for item in assessments
    ]

    selected_historical_task = st.selectbox(
        "Select task for historical analysis",
        historical_task_names,
        key="historical_risk_task",
    )

    historical_task_id = selected_historical_task.split(" | ", 1)[0]

    history = api_get(
        f"/api/v1/tasks/{historical_task_id}/risk-history"
    )

    trend = api_get(
        f"/api/v1/tasks/{historical_task_id}/risk-trend"
    )

    snapshots = history.get("snapshots", [])

    metric_cols = st.columns(6)

    with metric_cols[0]:
        st.metric(
            "Starting Risk",
            trend.get("starting_risk_score", "N/A"),
        )

    with metric_cols[1]:
        st.metric(
            "Current Risk",
            trend.get("current_risk_score", "N/A"),
        )

    with metric_cols[2]:
        risk_change = trend.get("risk_change")
        st.metric(
            "Risk Change",
            f"{risk_change:+d}" if risk_change is not None else "N/A",
        )

    with metric_cols[3]:
        velocity = trend.get("risk_velocity")
        st.metric(
            "Risk Velocity",
            f"{velocity:+.2f}" if velocity is not None else "N/A",
        )

    with metric_cols[4]:
        st.metric(
            "Trend",
            trend.get("trend", "N/A"),
        )

    with metric_cols[5]:
        st.metric(
            "Transition",
            trend.get("severity_transition", "N/A"),
        )

    st.markdown("#### Risk Trajectory")

    if snapshots:
        risk_scores = [
            snapshot.get("risk_score", 0)
            for snapshot in snapshots
        ]

        dates = [
            snapshot.get("snapshot_date", "")
            for snapshot in snapshots
        ]

        import pandas as pd

        trajectory_df = pd.DataFrame(
            {"Risk Score": risk_scores},
            index=pd.to_datetime(dates),
        )
        trajectory_df.index.name = "Date"

        st.line_chart(
            trajectory_df,
            height=280,
        )

        st.caption(
            f"Historical observation period: {dates[0]} → {dates[-1]}"
        )

        st.markdown("#### Historical Snapshots")

        snapshot_rows = [
        {
            "Date": snapshot.get("snapshot_date"),
            "Risk Score": snapshot.get("risk_score"),
            "Risk Level": snapshot.get("risk_level"),
        }
        for snapshot in snapshots
        ]

        st.dataframe(
        snapshot_rows,
        width="stretch",
        hide_index=True,
        )

    st.markdown("#### Executive Interpretation")

    starting_score = trend.get("starting_risk_score")
    current_score = trend.get("current_risk_score")
    risk_change = trend.get("risk_change")
    velocity = trend.get("risk_velocity")
    trend_name = trend.get("trend")
    transition = trend.get("severity_transition")

    if (
        starting_score is not None
        and current_score is not None
        and risk_change is not None
        and velocity is not None
    ):
        if risk_change > 0:
            direction = "increased"
        elif risk_change < 0:
            direction = "decreased"
        else:
            direction = "remained stable"

        st.info(
            f"{historical_task_id} risk {direction} from "
            f"{starting_score} to {current_score}, a net change of "
            f"{risk_change:+d} points. "
            f"The observed trend is **{trend_name}** with an average "
            f"movement of **{velocity:+.2f} points per snapshot**. "
            f"Severity transition: **{transition}**."
        )
else:
    st.info("No task history is available.")

st.subheader("Task Risk Explorer")

if assessments:
    task_names = [
        f"{item.get('task_id', '')} | {item.get('task_name', '')}"
        for item in assessments
    ]

    selected_task = st.selectbox(
        "Select a task",
        task_names,
    )

    selected_index = task_names.index(selected_task)
    task = assessments[selected_index]

    left, right = st.columns(2)

    with left:
        st.write(f"**Task:** {task.get('task_name', '')}")
        st.write(f"**Owner:** {task.get('owner', '')}")
        st.write(f"**Priority:** {task.get('priority', '')}")
        st.write(f"**Status:** {task.get('status', '')}")
        st.write(f"**Completion:** {task.get('completion', 0)}%")

    with right:
        score = task.get("risk_score", 0)
        level = task.get("risk_level", "Unknown")

        st.metric("Risk Score", score)
        st.write(f"**Risk Level:** {level}")

    st.markdown("#### Why is this task risky?")

    for reason in task.get("reasons", []):
        st.write(f"• {reason}")

    st.markdown("#### Recommended Actions")

    for recommendation in task.get("recommendations", []):
        st.write(f"• {recommendation}")


st.divider()

st.caption(
    f"Backend: FastAPI • API: {API_BASE_URL} • "
    "Demo data is synthetic"
)

# ------------------------------------------------------------
# M14 Decision Orchestration
with tabs[7]:
    st.subheader("Decision Orchestration")
    st.caption(
        "Multi-agent decision assessment · Evidence · Confidence · Review signal"
    )

    st.info(
        "Decision assessment only. No operational action is executed."
    )

    question = st.text_input(
        "Decision question",
        value="What should we review before proceeding with the deployment?",
        key="decision_question",
    )

    st.markdown("### Participating Agents")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Deployment", "Investigator")

    with c2:
        st.metric("Incident", "Investigator")

    with c3:
        st.metric("Release", "Governance")

    if st.button(
        "Build Decision Assessment",
        type="primary",
        use_container_width=True,
        key="decision_assessment_run",
    ):
        try:
            from app.models.copilot import CopilotIntent
            from app.services.copilot_orchestrator import orchestrate_skill

            with st.spinner("Running multi-agent decision assessment..."):
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

                payload = {
                    "question": question.strip(),
                    "intent": CopilotIntent.DEPLOYMENT.value,
                    "agent_results": [
                        {
                            "agent_id": "deployment-investigator",
                            "orchestration": deployment_result.model_dump(
                                mode="json"
                            ),
                        },
                        {
                            "agent_id": "incident-investigator",
                            "orchestration": incident_result.model_dump(
                                mode="json"
                            ),
                        },
                        {
                            "agent_id": "release-governance",
                            "orchestration": release_result.model_dump(
                                mode="json"
                            ),
                        },
                    ],
                }

                assessment = api_post(
                    "/copilot/decisions/orchestrate",
                    payload,
                )

                st.session_state["decision_assessment"] = assessment

        except Exception as exc:
            st.error(f"Decision assessment failed: {exc}")

    assessment = st.session_state.get("decision_assessment")

    if assessment:
        decision = assessment.get("decision", {})
        confidence = assessment.get("confidence", {})

        st.divider()
        st.markdown("### Decision Assessment")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Decision",
                decision.get(
                    "decision",
                    "N/A",
                ).replace("_", " ").title(),
            )

        with c2:
            st.metric(
                "Support Confidence",
                (
                    f"{confidence.get('score', 0)} · "
                    f"{confidence.get('level', 'none').upper()}"
                ),
            )

        with c3:
            review_required = assessment.get(
                "review_required",
                False,
            )

            st.metric(
                "Review Required",
                "Yes" if review_required else "No",
            )

        status = decision.get("status", "unknown")

        if status == "success":
            st.success(
                "Decision candidate generated successfully. "
                + confidence.get("rationale", "")
            )

        elif status == "partial_failure":
            st.warning(
                "Decision candidate contains partial results. "
                + confidence.get("rationale", "")
            )

        elif status == "blocked":
            st.error(
                "Decision is blocked because one or more "
                "agent contributions are blocked."
            )

        else:
            st.warning(
                "Insufficient evidence exists to support "
                "a decision candidate."
            )

        st.markdown("### Contributing Agents")

        agents = decision.get("contributing_agents", [])

        if agents:
            for agent_id in agents:
                st.write(f"• `{agent_id}`")
        else:
            st.write("No contributing agents.")

        left, right = st.columns(2)

        with left:
            st.markdown("### Evidence")

            evidence = decision.get("evidence", [])

            if evidence:
                for item in evidence:
                    st.write(f"• {item}")
            else:
                st.write("No evidence available.")

        with right:
            st.markdown("### Recommendations")

            recommendations = decision.get(
                "recommendations",
                [],
            )

            if recommendations:
                for item in recommendations:
                    st.write(f"• {item}")
            else:
                st.write("No recommendations available.")

        st.markdown("### Decision Rationale")
        st.write(
            decision.get(
                "rationale",
                "No rationale available.",
            )
        )

        st.markdown("### Execution Trace")

        for step in assessment.get("trace", []):
            st.write(f"✓ {step}")

        st.caption(
            "M14 · Multi-Agent Decision Orchestration · "
            "Synthetic demo data · Read-only"
        )


# M15 Human Approval Governance
with tabs[8]:
    st.subheader("Human Approval Governance")
    st.caption(
        "Decision → Human Approval → Audit Trail"
    )

    st.warning(
        "No operational action is executed by this cockpit. "
        "Approval only changes governance eligibility."
    )

    assessment = st.session_state.get("m14_decision_assessment")

    if not assessment:
        st.info(
            "Build a Decision Assessment in the 🧭 Decisions tab first."
        )
    else:
        decision = assessment.get("decision", {})
        confidence = assessment.get("confidence", {})

        st.markdown("### Decision Under Review")

        a1, a2, a3 = st.columns(3)

        with a1:
            st.metric(
                "Decision Status",
                decision.get("status", "unknown").upper(),
            )

        with a2:
            st.metric(
                "Confidence",
                (
                    f"{confidence.get('score', 0)} · "
                    f"{confidence.get('level', 'none').upper()}"
                ),
            )

        with a3:
            st.metric(
                "Action Required",
                "Yes"
                if decision.get("action_required", False)
                else "No",
            )

        st.markdown("### Human Review")

        reviewer = st.text_input(
            "Reviewer",
            value="human-reviewer",
            key="m15_reviewer",
        )

        approval_decision = st.radio(
            "Approval decision",
            [
                "Pending",
                "Approved",
                "Rejected",
            ],
            horizontal=True,
            key="m15_approval_decision",
        )

        approval_comment = st.text_area(
            "Approval comment",
            value="",
            placeholder=(
                "Record the rationale for the human decision."
            ),
            key="m15_approval_comment",
        )

        if st.button(
            "Submit Governance Decision",
            type="primary",
            use_container_width=True,
            key="m15_submit_approval",
        ):
            try:
                decision_id = st.text_input(
                    "Decision ID",
                    value="DEC-STREAMLIT-001",
                    key="m15_decision_id",
                )

                payload = {
                    "assessment": assessment,
                    "approver": (
                        None
                        if approval_decision == "Pending"
                        else reviewer.strip()
                    ),
                    "approval_comment": (
                        None
                        if approval_decision == "Pending"
                        else (
                            f"{approval_decision}: "
                            f"{approval_comment.strip()}"
                        )
                    ),
                }

                with st.spinner("Evaluating governance decision..."):
                    result = api_post(
                        f"/copilot/decisions/{decision_id}/approval",
                        payload,
                    )

                st.session_state["m15_approval_result"] = result

            except Exception as exc:
                st.error(
                    f"Governance decision failed: {exc}"
                )

        approval_result = st.session_state.get(
            "m15_approval_result"
        )

        if approval_result:
            st.divider()

            approval = approval_result.get("approval", {})
            audit = approval_result.get("audit_record", {})

            g1, g2, g3 = st.columns(3)

            with g1:
                status = approval.get("status", "unknown")

                if status == "approved":
                    st.success("APPROVED")
                elif status == "rejected":
                    st.error("REJECTED")
                else:
                    st.warning("PENDING")

            with g2:
                st.metric(
                    "Allowed to Proceed",
                    "Yes"
                    if approval.get("allowed_to_proceed", False)
                    else "No",
                )

            with g3:
                st.metric(
                    "Approval Required",
                    "Yes"
                    if approval.get("approval_required", False)
                    else "No",
                )

            st.markdown("### Governance Rationale")
            st.write(
                approval.get(
                    "rationale",
                    "No rationale available.",
                )
            )

            st.markdown("### Approval Audit Record")

            st.write(
                f"**Audit ID:** `{audit.get('audit_id', 'N/A')}`"
            )
            st.write(
                f"**Decision ID:** `{audit.get('decision_id', 'N/A')}`"
            )
            st.write(
                f"**Status:** `{audit.get('status', 'N/A')}`"
            )

            if audit.get("approver"):
                st.write(
                    f"**Approver:** {audit['approver']}"
                )

            if audit.get("approval_comment"):
                st.write(
                    f"**Comment:** {audit['approval_comment']}"
                )

            st.write(
                f"**Allowed to Proceed:** "
                f"{'Yes' if audit.get('allowed_to_proceed') else 'No'}"
            )

            st.markdown("### Governance Trace")

            for step in approval_result.get("trace", []):
                st.write(f"✓ {step}")

        try:
            audit_summary = api_get(
                "/copilot/approvals/audit/summary"
            )

            st.divider()
            st.markdown("### Approval Audit Summary")

            s1, s2, s3, s4 = st.columns(4)

            with s1:
                st.metric(
                    "Total",
                    audit_summary.get("total_records", 0),
                )

            with s2:
                st.metric(
                    "Pending",
                    audit_summary.get("pending", 0),
                )

            with s3:
                st.metric(
                    "Approved",
                    audit_summary.get("approved", 0),
                )

            with s4:
                st.metric(
                    "Rejected",
                    audit_summary.get("rejected", 0),
                )

        except Exception:
            pass

        st.caption(
            "M15 · Human Approval & Governance · "
            "Synthetic demo data · No autonomous execution"
        )


# Copilot
# ------------------------------------------------------------

with tabs[6]:
    st.subheader("SAP Cloud ALM Copilot")
    st.caption(
        "Grounded operational assistance with conversation context, "
        "entity resolution, evidence continuity, and governed actions."
    )

    if "copilot_conversation_id" not in st.session_state:
        st.session_state.copilot_conversation_id = "streamlit-demo"

    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = []

    if "copilot_question" not in st.session_state:
        st.session_state.copilot_question = ""

    col1, col2 = st.columns([4, 1])

    with col1:
        conversation_id = st.text_input(
            "Conversation ID",
            value=st.session_state.copilot_conversation_id,
            key="copilot_conversation_id_input",
        )

    with col2:
        st.write("")
        if st.button("Reset", key="copilot_reset"):
            st.session_state.copilot_messages = []
            st.session_state.copilot_conversation_id = "streamlit-demo"
            st.session_state.copilot_question = ""
            st.rerun()

    st.session_state.copilot_conversation_id = conversation_id

    suggestions = [
        "Why was the deployment rolled back?",
        "What incident caused it?",
        "What should we review first?",
    ]

    st.markdown("**Suggested questions**")

    suggestion_cols = st.columns(3)

    for index, suggestion in enumerate(suggestions):
        with suggestion_cols[index]:
            if st.button(
                suggestion,
                key=f"copilot_suggestion_{index}",
                use_container_width=True,
            ):
                st.session_state.copilot_question = suggestion
                st.rerun()

    question = st.text_input(
        "Ask Copilot",
        placeholder=(
            "Ask about delivery health, incidents, problems, "
            "changes, releases, deployments, or recommendations..."
        ),
        key="copilot_question",
    )

    if st.button(
        "Ask Copilot",
        type="primary",
        key="copilot_ask",
        use_container_width=True,
    ):
        if not question.strip():
            st.warning("Enter a question before asking Copilot.")
        else:
            try:
                response = _local_client.post(
                    "/copilot/query",
                    json={
                        "conversation_id": conversation_id,
                        "question": question.strip(),
                    },
                )

                response.raise_for_status()

                st.session_state.copilot_messages.append(
                    {
                        "question": question.strip(),
                        "response": response.json(),
                    }
                )

            except Exception as exc:
                st.error(f"Copilot request failed: {exc}")

    if st.session_state.copilot_messages:
        st.divider()
        st.markdown("### Conversation")

        for message in st.session_state.copilot_messages:
            result = message["response"]

            st.markdown(
                f"**You:** {message['question']}"
            )

            st.markdown(
                f"**Copilot:** "
                f"{result.get('answer', 'No answer returned.')}"
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Intent",
                    result.get("intent", "unknown"),
                )

            with c2:
                st.metric(
                    "Grounded",
                    "Yes" if result.get("grounded") else "No",
                )

            with c3:
                st.metric(
                    "Approval",
                    (
                        "Required"
                        if result.get("approval_required")
                        else "Not required"
                    ),
                )

            evidence = result.get("evidence", [])

            if evidence:
                with st.expander(
                    f"Evidence ({len(evidence)})",
                    expanded=True,
                ):
                    for item in evidence:
                        st.write(f"• {item}")

            trace = result.get("trace", [])

            if trace:
                with st.expander(
                    "Execution Trace",
                    expanded=False,
                ):
                    for item in trace:
                        st.write(f"• {item}")

            st.divider()
