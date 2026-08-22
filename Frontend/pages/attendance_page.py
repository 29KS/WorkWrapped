import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from styles import dark_chart_layout

API_BASE = os.getenv(
    "API_BASE",
    "http://localhost:8000"
)

@st.cache_data(ttl=60, show_spinner=False)  # cache for 60s, tune as needed
def fetch_work_statistics(uid):
    res = requests.get(f"{API_BASE}/employees/{uid}/attendance")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">🗓️ Attendance Insights</div>',
                unsafe_allow_html=True)
    res = requests.get(f"{API_BASE}/employees/{uid}/attendance")
    if res.status_code != 200:
        st.error("Data not found")
        return
    data = res.json()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: KPIs ───────────────────────────────────────────
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Attendance %",  f"{data['attendance_percentage']}%")
    c2.metric("Present Days",  data["present_days"])
    c3.metric("Leave Days",    data["leave_days"])
    c4.metric("Late Arrivals", data["late_arrivals"])
    c5.metric("Avg Hours",     f"{data['working_hours']['average_hours']}h")
    c6.metric("Total Hours",   f"{data['working_hours']['total_hours']}h")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 2: Pie + Bar ──────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Present vs Leave</div>',
                    unsafe_allow_html=True)
        fig1 = px.pie(pd.DataFrame({
            "Category": ["Present","Leave"],
            "Days": [data["present_days"], data["leave_days"]]
        }), names="Category", values="Days", hole=0.5,
            color_discrete_sequence=["#2ecc71","#e74c3c"])
        fig1.update_layout(dark_chart_layout(""), height=260)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Attendance Alerts</div>',
                    unsafe_allow_html=True)
        fig2 = px.bar(pd.DataFrame({
            "Category": ["Late","Short Days","Missed","Idle","Geo Range"],
            "Count": [
                data["late_arrivals"], data["short_days"],
                data["missed_checkouts"], data["idle_warning_days"],
                data["geo_out_of_range_days"]
            ]
        }), x="Category", y="Count", color="Category", text="Count",
            color_discrete_sequence=["#e94560","#f39c12","#e67e22","#9b59b6","#3498db"])
        fig2.update_layout(dark_chart_layout(""), showlegend=False, height=260)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Check-in/out + Hours comparison ────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">Check-In / Check-Out</div>',
                    unsafe_allow_html=True)
        t1,t2,t3,t4 = st.columns(2), st.columns(2), None, None
        r1,r2 = st.columns(2)
        r1.metric("Earliest Check-in",  data["checkin_checkout"]["earliest_checkin"])
        r2.metric("Latest Check-out",   data["checkin_checkout"]["latest_checkout"])
        r3,r4 = st.columns(2)
        r3.metric("Missed Checkouts",   data["missed_checkouts"])
        r4.metric("Short Days",         data["short_days"])

    with col4:
        st.markdown('<div class="section-title">Working Hours Overview</div>',
                    unsafe_allow_html=True)
        fig3 = px.bar(pd.DataFrame({
            "Type":  ["Average Hours/Day","Total Hours"],
            "Hours": [data["working_hours"]["average_hours"],
                      data["working_hours"]["total_hours"]]
        }), x="Type", y="Hours", color="Type", text="Hours",
            color_discrete_sequence=["#e94560","#0f3460"])
        fig3.update_layout(dark_chart_layout(""), showlegend=False, height=220)
        st.plotly_chart(fig3, use_container_width=True)