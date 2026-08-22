import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from styles import dark_chart_layout

API_BASE = os.getenv(
    "API_BASE",
    "http://localhost:8000"
)

@st.cache_data(ttl=60, show_spinner=False)  # cache for 60s, tune as needed
def fetch_work_statistics(uid):
    res = requests.get(f"{API_BASE}/employees/{uid}/productivity")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">⚡ Productivity Insights</div>', unsafe_allow_html=True)

    res = requests.get(f"{API_BASE}/employees/{uid}/productivity")
    if res.status_code != 200:
        st.error("Employee not found")
        return

    data = res.json()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: KPI Cards ─────────────────────────────────────
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Most Productive Day", data.get("most_productive_day", "N/A"))
    c2.metric("Longest Streak", f"{data.get('longest_working_streak', 0)} days")
    c3.metric("Avg Tasks / Day", data.get("average_tasks_per_day", 0))
    fastest = data.get("fastest_task")
    c4.metric("Fastest Task", f"{fastest['actualHours']}h" if fastest else "N/A")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    trend = data.get("productivity_trend", [])
    dist = data.get("completion_time_distribution", [])

    # ── Row 2: Line + Bar side by side ───────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Productivity Trend</div>', unsafe_allow_html=True)
        if trend:
            df_trend = pd.DataFrame(trend)
            df_trend["date"] = pd.to_datetime(df_trend["date"])
            fig1 = px.line(df_trend, x="date", y="tasks", markers=True,
                           labels={"date": "Date", "tasks": "Tasks"})
            fig1.update_traces(line_color="#e94560", marker_color="#e94560")
            fig1.update_layout(dark_chart_layout("Daily Completions"))
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Avg Tasks by Day of Week</div>', unsafe_allow_html=True)
        if trend:
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            df_trend["day_of_week"] = df_trend["date"].dt.strftime("%A")
            day_avg = (df_trend.groupby("day_of_week")["tasks"]
                       .mean().reindex(day_order).fillna(0).reset_index())
            day_avg.columns = ["Day", "Avg Tasks"]
            fig2 = px.bar(day_avg, x="Day", y="Avg Tasks", color="Avg Tasks",
                          color_continuous_scale="Teal")
            fig2.update_layout(dark_chart_layout("Avg Tasks per Day"))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Histogram + Heatmap side by side ───────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Task Completion Time Distribution</div>', unsafe_allow_html=True)
        if dist:
            df_dist = pd.DataFrame(dist)
            fig3 = px.histogram(df_dist, x="actualHours", nbins=10,
                                labels={"actualHours": "Hours Taken"},
                                color_discrete_sequence=["#e94560"])
            fig3.update_traces(marker_line_color="#0f0f0f", marker_line_width=1)
            fig3.update_layout(dark_chart_layout("Completion Time Distribution"))
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Activity Heatmap</div>', unsafe_allow_html=True)
        if trend:
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            df_trend["week"] = df_trend["date"].dt.isocalendar().week.astype(int)
            df_trend["day_of_week"] = df_trend["date"].dt.strftime("%A")
            heatmap_data = df_trend.pivot_table(
                index="day_of_week", columns="week",
                values="tasks", aggfunc="sum", fill_value=0
            ).reindex(day_order).fillna(0).astype(int)

            fig4 = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=[f"W{w}" for w in heatmap_data.columns],
                y=heatmap_data.index.tolist(),
                colorscale="YlGnBu",
                text=heatmap_data.values,
                texttemplate="%{text}",
                hovertemplate="Day: %{y}<br>%{x}<br>Tasks: %{z}<extra></extra>"
            ))
            fig4.update_layout(dark_chart_layout("Tasks by Day & Week"))
            st.plotly_chart(fig4, use_container_width=True)