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


def health_color(health: str) -> str:
    return {
        "Green": "🟢",
        "Amber": "🟠",
        "Red": "🔴",
    }.get(health, "⚪")


st.title("SAP Cloud ALM AI Copilot")
st.caption("Delivery Intelligence • Risk • Health • Early Warnings")

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
