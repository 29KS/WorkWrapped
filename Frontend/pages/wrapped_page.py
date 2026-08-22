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
    res = requests.get(f"{API_BASE}/employees/{uid}/wrapped")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown("""
    <div style="text-align:center; padding:12px 0 8px;">
        <div style="font-size:26px; font-weight:900; color:#fff;">⚡ WorkWrapped- MyWorkStory</div>
        <div style="font-size:12px; color:#555; margin-top:2px;">
            Your internship in numbers — powered by AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✨ Generate My Wrapped", type="primary", use_container_width=False):
        st.session_state["wrapped_data"] = None
        with st.spinner("Generating your wrapped report..."):
            res = requests.get(f"{API_BASE}/employees/{uid}/wrapped")
        if res.status_code == 200:
            st.session_state["wrapped_data"] = res.json()
        else:
            st.error("Could not generate wrapped report")
            return

    wrapped = st.session_state.get("wrapped_data")
    if not wrapped:
        st.markdown("""
        <div style="text-align:center; padding:60px 0; color:#444; font-size:14px;">
            Click the button above to generate your personalized wrapped report ✨
        </div>
        """, unsafe_allow_html=True)
        return

    pred  = wrapped["predictions"]
    stats = wrapped["stats"]
    gc    = {"A+":"#2ecc71","A":"#27ae60","B":"#f39c12","C":"#e67e22","D":"#e74c3c"}.get(pred["performance_grade"],"#888")
    rc    = {"Low":"#2ecc71","Medium":"#f39c12","High":"#e74c3c"}.get(pred["burnout_risk"],"#888")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: Hero + AI Summary ──────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
                    border:1px solid #e9456040; border-radius:14px;
                    padding:20px; text-align:center; height:100%;">
            <div style="font-size:44px;">{pred['personality_emoji']}</div>
            <div style="font-size:18px; font-weight:800; color:#fff; margin-top:8px;">
                {wrapped['name']}
            </div>
            <div style="font-size:11px; color:#888;">
                {wrapped['position']} · {wrapped['department']}
            </div>
            <hr style="border-color:#2a2a4a; margin:10px 0;">
            <div style="font-size:12px; color:#ccc; margin-bottom:8px;">
                🎭 {pred['personality']}
            </div>
            <span style="background:{gc}18; color:{gc}; padding:4px 12px;
                         border-radius:20px; font-size:12px; border:1px solid {gc}40;">
                Grade {pred['performance_grade']} · {pred['performance_score']} / 100
            </span>
            <br><br>
            <span style="background:{rc}18; color:{rc}; padding:4px 12px;
                         border-radius:20px; font-size:12px; border:1px solid {rc}40;">
                Burnout: {pred['burnout_risk']}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">✨ AI Generated Summary</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);
                    border:1px solid #e9456030; border-radius:12px;
                    padding:20px; font-size:14px; color:#ddd;
                    line-height:1.9; font-style:italic; height:90%;">
            {wrapped['summary']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 2: 8 KPI stats ────────────────────────────────────
    st.markdown('<div class="section-title">Internship in Numbers</div>',
                unsafe_allow_html=True)
    k1,k2,k3,k4,k5,k6,k7,k8 = st.columns(8)
    k1.metric("Tasks Done",    stats["tasks_completed"])
    k2.metric("Completion %",  f"{stats['completion_rate']}%")
    k3.metric("On-Time %",     f"{stats['ontime_pct']}%")
    k4.metric("Attendance %",  f"{stats['attendance_pct']}%")
    k5.metric("Avg Hours",     f"{stats['avg_hours']}h")
    k6.metric("Total Hours",   f"{stats['total_hours']}h")
    k7.metric("Projects",      stats["projects"])
    k8.metric("Pending",       stats["pending_tasks"])

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Charts ─────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="section-title">Phase Progress</div>',
                    unsafe_allow_html=True)
        phases = wrapped.get("phases",[])
        if phases:
            df_p = pd.DataFrame(phases)
            df_p.columns = ["Phase","Total","Done"]
            df_p["Phase"] = df_p["Phase"].str[:15]
            fig1 = px.bar(df_p, x="Phase", y=["Done","Total"],
                          barmode="group",
                          color_discrete_sequence=["#2ecc71","#e94560"])
            fig1.update_layout(dark_chart_layout(""), height=240)
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Task Breakdown</div>',
                    unsafe_allow_html=True)
        fig2 = px.pie(pd.DataFrame({
            "Status": ["Completed","Pending"],
            "Count":  [stats["tasks_completed"], stats["pending_tasks"]]
        }), names="Status", values="Count", hole=0.55,
            color_discrete_sequence=["#2ecc71","#e94560"])
        fig2.update_layout(dark_chart_layout(""), height=240)
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown('<div class="section-title">Key Metrics</div>',
                    unsafe_allow_html=True)
        fig3 = px.bar(pd.DataFrame({
            "Metric": ["Attendance","Completion","On-Time"],
            "Value":  [stats["attendance_pct"],stats["completion_rate"],stats["ontime_pct"]]
        }), x="Metric", y="Value", color="Metric", text="Value",
            color_discrete_sequence=["#3498db","#2ecc71","#f39c12"])
        fig3.update_layout(dark_chart_layout(""), height=240, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)