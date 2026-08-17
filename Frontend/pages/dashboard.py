import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor
from styles import dark_chart_layout

API_BASE = "http://localhost:8000"

ENDPOINTS = {
    "emp":  "",
    "tp":   "/work-statistics",
    "att":  "/attendance",
    "perf": "/performance-score",
    "burn": "/burnout",
    "pers": "/personality",
    "prod": "/productivity",
}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_dashboard_data(uid):
    def fetch_one(suffix):
        url = f"{API_BASE}/employees/{uid}{suffix}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else {}
        except requests.RequestException:
            return {}

    with ThreadPoolExecutor(max_workers=len(ENDPOINTS)) as pool:
        results = dict(zip(
            ENDPOINTS.keys(),
            pool.map(fetch_one, ENDPOINTS.values())
        ))
    return results


def show(uid):
    d = fetch_dashboard_data(uid)
    emp, tp, att, perf, burn, pers, prod = (
        d["emp"], d["tp"], d["att"], d["perf"], d["burn"], d["pers"], d["prod"]
    )

    name  = st.session_state.get("email","").split("@")[0].title()
    grade = perf.get("grade","N/A")
    gc    = {"A+":"#2ecc71","A":"#27ae60","B":"#f39c12","C":"#e67e22","D":"#e74c3c"}.get(grade,"#888")
    risk  = burn.get("risk_level","N/A")
    rc    = {"Low":"#2ecc71","Medium":"#f39c12","High":"#e74c3c"}.get(risk,"#888")

    # ── Welcome banner ────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);
                border:1px solid #e9456030; border-radius:14px;
                padding:20px 24px; margin-bottom:12px;">
        <div style="font-size:20px; font-weight:800; color:#fff;">
            👋 Welcome back, {name}!
        </div>
        <div style="font-size:12px; color:#888; margin-top:4px;">
            {emp.get("position","")} · {emp.get("department","")} · {emp.get("workMode","")}
        </div>
        <div style="margin-top:14px; display:flex; gap:10px; flex-wrap:wrap;">
            <span style="background:{gc}18; color:{gc}; padding:4px 14px;
                         border-radius:20px; font-size:12px; border:1px solid {gc}40;">
                Grade {grade} · {perf.get("predicted_score","N/A")} / 100
            </span>
            <span style="background:{rc}18; color:{rc}; padding:4px 14px;
                         border-radius:20px; font-size:12px; border:1px solid {rc}40;">
                {burn.get("risk_label","Burnout: N/A")}
            </span>
            <span style="background:#e9456018; color:#e94560; padding:4px 14px;
                         border-radius:20px; font-size:12px; border:1px solid #e9456040;">
                {pers.get("emoji","")} {pers.get("personality","N/A")}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Quick Stats</div>',
                unsafe_allow_html=True)
    k1,k2,k3,k4,k5,k6,k7,k8 = st.columns(8)
    k1.metric("Tasks Done",   tp.get("completed_tasks",0))
    k2.metric("Pending",      tp.get("pending_tasks",0))
    k3.metric("Completion",   f"{tp.get('completion_rate',0)}%")
    k4.metric("Attendance",   f"{att.get('attendance_percentage',0)}%")
    k5.metric("Avg Hours",    f"{att.get('working_hours',{}).get('average_hours',0)}h")
    k6.metric("Projects",     tp.get("total_projects",0))
    k7.metric("Perf Score",   perf.get("predicted_score","N/A"))
    k8.metric("Subtasks",     f"{tp.get('subtask_completion_rate',0)}%")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="section-title">Productivity Trend</div>',
                    unsafe_allow_html=True)
        trend = prod.get("productivity_trend", [])
        if trend:
            df_t = pd.DataFrame(trend)
            df_t["date"] = pd.to_datetime(df_t["date"])
            fig1 = px.line(df_t, x="date", y="tasks", markers=True)
            fig1.update_traces(line_color="#e94560", marker_color="#e94560")
            fig1.update_layout(dark_chart_layout(""), height=220,
                               margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Task Breakdown</div>',
                    unsafe_allow_html=True)
        fig2 = px.pie(pd.DataFrame({
            "Status": ["Done","Pending"],
            "Count":  [tp.get("completed_tasks",0), tp.get("pending_tasks",0)]
        }), names="Status", values="Count", hole=0.55,
            color_discrete_sequence=["#2ecc71","#e94560"])
        fig2.update_layout(dark_chart_layout(""), height=220,
                           margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown('<div class="section-title">Attendance Flags</div>',
                    unsafe_allow_html=True)
        fig3 = px.bar(pd.DataFrame({
            "Flag":  ["Late","Short","Missed","Idle","Geo"],
            "Count": [
                att.get("late_arrivals",0),
                att.get("short_days",0),
                att.get("missed_checkouts",0),
                att.get("idle_warning_days",0),
                att.get("geo_out_of_range_days",0)
            ]
        }), x="Flag", y="Count", color="Flag", text="Count",
            color_discrete_sequence=["#e94560","#f39c12","#e67e22","#9b59b6","#3498db"])
        fig3.update_layout(dark_chart_layout(""), height=220,
                           showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Quick nav ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Quick Navigate</div>',
                unsafe_allow_html=True)
    pages = [
        ("📊","Work Stats","work_statistics"),
        ("⚡","Productivity","productivity"),
        ("🎯","Performance","performance"),
        ("🏆","Achievements","achievements"),
        ("✨","My Wrapped","wrapped"),
    ]
    cols = st.columns(5)
    for (icon,label,key), col in zip(pages, cols):
        with col:
            if st.button(f"{icon} {label}", use_container_width=True):
                st.session_state["page"] = key
                st.query_params.update({"page": key})
                st.rerun()