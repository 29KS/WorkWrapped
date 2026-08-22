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
    res = requests.get(f"{API_BASE}/employees/{uid}/achievements")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">🏆 Achievement & Leaderboard</div>',
                unsafe_allow_html=True)
    res = requests.get(f"{API_BASE}/employees/{uid}/achievements")
    if res.status_code != 200:
        st.error("Data not found")
        return
    data = res.json()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: KPIs ───────────────────────────────────────────
    st.markdown('<div class="section-title">Performance Score</div>',
                unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Overall Score",    f"{data['score']} / 100")
    c2.metric("Completion Rate",  f"{data['completion_rate']}%")
    c3.metric("On-Time Rate",     f"{data['ontime_rate']}%")
    c4.metric("Attendance Rate",  f"{data['attendance_rate']}%")
    c5.metric("Company Rank",     f"#{data['rank_in_company']}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 2: Badges ─────────────────────────────────────────
    st.markdown('<div class="section-title">Achievements Unlocked</div>',
                unsafe_allow_html=True)
    achievements = data.get("achievements", [])
    if achievements:
        cols = st.columns(len(achievements))
        for i, ach in enumerate(achievements):
            with cols[i]:
                st.markdown(f"""
                <div class="ach-card">
                    <div style="font-size:28px;">🏆</div>
                    <div style="font-weight:700; margin-top:8px; font-size:13px;">
                        {ach['title']}
                    </div>
                    <div style="font-size:11px; color:#aaa; margin-top:4px;">
                        {ach['description']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No achievements yet")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Leaderboard ────────────────────────────────────
    lb_res = requests.get(f"{API_BASE}/leaderboard")
    if lb_res.status_code == 200:
        lb = lb_res.json()
        df = pd.DataFrame(lb)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">Employee Scores</div>',
                        unsafe_allow_html=True)
            fig1 = px.bar(df.sort_values("score"), x="score", y="name",
                          orientation="h", color="score",
                          color_continuous_scale="Blues")
            fig1.update_layout(dark_chart_layout(""), height=280)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Score Breakdown</div>',
                        unsafe_allow_html=True)
            df_melt = df.melt(
                id_vars=["name"],
                value_vars=["completion_rate","ontime_rate","attendance_rate"],
                var_name="Metric", value_name="Value"
            )
            fig2 = px.bar(df_melt, x="name", y="Value", color="Metric",
                          barmode="group",
                          color_discrete_sequence=["#e94560","#f39c12","#2ecc71"])
            fig2.update_layout(dark_chart_layout(""), height=280)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Rankings Table</div>',
                    unsafe_allow_html=True)
        df_d = df[["rank","name","score","completion_rate","ontime_rate","attendance_rate","assessment_score"]].copy()
        df_d.columns = ["Rank","Name","Score","Completion %","On-Time %","Attendance %","Assessment"]
        st.dataframe(df_d, use_container_width=True, hide_index=True)