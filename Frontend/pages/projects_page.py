import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from styles import dark_chart_layout

API_BASE = "http://localhost:8000"

@st.cache_data(ttl=60, show_spinner=False)  # cache for 60s, tune as needed
def fetch_work_statistics(uid):
    res = requests.get(f"{API_BASE}/employees/{uid}/projects")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">📁 Projects Done</div>',
                unsafe_allow_html=True)
    res = requests.get(f"{API_BASE}/employees/{uid}/projects")
    if res.status_code != 200:
        st.error("Data not found")
        return
    data = res.json()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: KPIs ───────────────────────────────────────────
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Projects",       data.get("total_projects",0))
    c2.metric("Biggest Project",      data.get("biggest_project","N/A"))
    c3.metric("Highest Contribution", data.get("highest_contribution","N/A"))
    c4.metric("Most Active",          data.get("most_active_project","N/A"))

    completed = data.get("completed_projects",[])
    st.markdown(
        f'<div style="font-size:12px;color:#aaa;margin:4px 0;">✅ Completed: '
        f'<span style="color:#2ecc71;">{", ".join(completed) if completed else "None yet"}</span></div>',
        unsafe_allow_html=True
    )
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    task_stats = data.get("task_project_stats",[])
    if task_stats:
        df = pd.DataFrame(task_stats)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">Contribution per Project</div>',
                        unsafe_allow_html=True)
            fig1 = px.bar(df.sort_values("actualHours"), x="actualHours", y="project",
                          orientation="h", color="actualHours",
                          color_continuous_scale="Teal")
            fig1.update_layout(dark_chart_layout(""), height=280)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Time Share per Project</div>',
                        unsafe_allow_html=True)
            fig2 = px.pie(df, values="actualHours", names="project", hole=0.4)
            fig2.update_layout(dark_chart_layout(""), height=280)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Tasks Done vs Total</div>',
                    unsafe_allow_html=True)
        fig3 = px.bar(df, x="project", y=["doneTasks","totalTasks"],
                      barmode="group",
                      color_discrete_sequence=["#2ecc71","#e94560"])
        fig3.update_layout(dark_chart_layout(""), height=240)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Prior Projects</div>',
                unsafe_allow_html=True)
    prior = data.get("prior_projects",[])
    cols  = st.columns(3)
    for i, proj in enumerate(prior):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="text-align:left; margin-bottom:10px; min-height:90px;">
                <div style="font-size:13px; font-weight:600; color:#fff;">
                    📁 {proj['title']}
                </div>
                <div style="font-size:11px; color:#aaa; margin-top:6px; line-height:1.5;">
                    {proj.get('description','')[:120]}...
                </div>
            </div>
            """, unsafe_allow_html=True)