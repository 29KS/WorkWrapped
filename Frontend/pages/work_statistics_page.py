import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from styles import dark_chart_layout
import os

API_BASE = os.getenv(
    "API_BASE",
    "http://localhost:8000"
)

@st.cache_data(ttl=60, show_spinner=False)  # cache for 60s, tune as needed
def fetch_work_statistics(uid):
    res = requests.get(f"{API_BASE}/employees/{uid}/work-statistics")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">📊 Work Statistics</div>', unsafe_allow_html=True)

    res = requests.get(f"{API_BASE}/employees/{uid}/work-statistics")
    if res.status_code != 200:
        st.error("Employee not found")
        return

    data = res.json()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: KPI Cards ─────────────────────────────────────
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Tasks", data["total_tasks"])
    c2.metric("Completed", data["completed_tasks"])
    c3.metric("Pending", data["pending_tasks"])
    c4.metric("Overdue", data["overdue_tasks"])
    c5.metric("Completion %", f"{data['completion_rate']}%")
    c6.metric("Projects", data["total_projects"])

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 2: Bar + Pie side by side ────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Task Distribution</div>', unsafe_allow_html=True)
        status_df = pd.DataFrame({
            "Status": ["Completed", "Pending", "Overdue"],
            "Tasks": [data["completed_tasks"], data["pending_tasks"], data["overdue_tasks"]]
        })
        fig1 = px.bar(status_df, x="Status", y="Tasks", color="Status", text="Tasks",
                      color_discrete_sequence=["#2ecc71", "#f39c12", "#e74c3c"])
        fig1.update_layout(dark_chart_layout("Task Status"), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Completed vs Pending</div>', unsafe_allow_html=True)
        pie_df = pd.DataFrame({
            "Status": ["Completed", "Pending", "Overdue"],
            "Count": [data["completed_tasks"], data["pending_tasks"], data["overdue_tasks"]]
        })
        fig2 = px.pie(pie_df, names="Status", values="Count", hole=0.45,
                      color_discrete_sequence=["#2ecc71", "#f39c12", "#e74c3c"])
        fig2.update_layout(dark_chart_layout("Task Completion"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Hours + Subtasks ───────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Estimated vs Actual Hours</div>', unsafe_allow_html=True)
        hours = data["hours_comparison"]
        hours_df = pd.DataFrame({
            "Type": ["Estimated Hours", "Actual Hours"],
            "Hours": [hours["estimated_hours"], hours["actual_hours"]]
        })
        fig3 = px.bar(hours_df, x="Type", y="Hours", color="Type", text="Hours",
                      color_discrete_sequence=["#e94560", "#0f3460"])
        fig3.update_layout(dark_chart_layout("Hours Comparison"), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Subtask Completion</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(data["subtask_completion_rate"] / 100)
        s1, s2, s3 = st.columns(3)
        s1.metric("Completed", data["completed_subtasks"])
        s2.metric("Total", data["total_subtasks"])
        s3.metric("Rate", f"{data['subtask_completion_rate']}%")

        # summary table
        st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Metric": ["Avg Hours/Task", "Total Est. Hours", "Total Actual Hours"],
            "Value": [
                data["average_actual_hours_per_task"],
                data["total_estimated_hours"],
                data["total_actual_hours"]
            ]
        })
        st.dataframe(summary, use_container_width=True, hide_index=True)