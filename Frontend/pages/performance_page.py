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
    res = requests.get(f"{API_BASE}/employees/{uid}/performance")
    res_score = requests.get(f"{API_BASE}/employees/{uid}/performance-score")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">🎯 Performance Insights</div>', unsafe_allow_html=True)

    res       = requests.get(f"{API_BASE}/employees/{uid}/performance")
    res_score = requests.get(f"{API_BASE}/employees/{uid}/performance-score")

    if res.status_code != 200:
        st.error("Employee not found")
        return

    data = res.json()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: KPI Cards ─────────────────────────────────────
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Before Deadline",   data["tasks_completed_before_deadline"])
    c2.metric("Delayed Tasks",     data["delayed_tasks"])
    c3.metric("On-Time Delivery",  f"{data['on_time_delivery_percentage']}%")
    c4.metric("Performance Score", f"{data['overall_performance_score']}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 2: Pie + Radar + Weekly Trend ────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="section-title">On-Time vs Delayed</div>',
                    unsafe_allow_html=True)
        pie_df = pd.DataFrame({
            "Category": ["On-Time", "Delayed"],
            "Tasks": [data["tasks_completed_before_deadline"], data["delayed_tasks"]]
        })
        fig1 = px.pie(pie_df, names="Category", values="Tasks", hole=0.45,
                      color_discrete_sequence=["#2ecc71", "#e74c3c"])
        fig1.update_layout(dark_chart_layout("Task Completion Status"), height=280)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Performance Radar</div>',
                    unsafe_allow_html=True)
        metrics    = data["performance_metrics"]
        categories = ["On-Time Tasks", "Delayed Tasks", "On-Time %", "Perf Score"]
        values     = [
            metrics["on_time_tasks"],
            metrics["delayed_tasks"],
            metrics["on_time_delivery_percentage"],
            metrics["overall_performance_score"]
        ]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatterpolar(
            r=values, theta=categories, fill="toself",
            line_color="#e94560", fillcolor="rgba(233,69,96,0.2)"
        ))
        fig2.update_layout(
            dark_chart_layout(""),
            polar=dict(
                bgcolor="#1a1a2e",
                radialaxis=dict(visible=True, color="#888"),
                angularaxis=dict(color="#888")
            ),
            showlegend=False, height=280,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown('<div class="section-title">Weekly Performance Trend</div>',
                    unsafe_allow_html=True)
        weekly = pd.DataFrame(data["weekly_consistency"])
        fig3   = px.line(weekly, x="week", y="completed_tasks", markers=True,
                         labels={"week": "Phase", "completed_tasks": "Tasks"})
        fig3.update_traces(line_color="#e94560", marker_color="#e94560")
        fig3.update_layout(dark_chart_layout("Tasks Across Phases"), height=280)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Overall Score Bar (full width, compact) ────────
    st.markdown('<div class="section-title">Overall Score</div>', unsafe_allow_html=True)
    score_df = pd.DataFrame({
        "Metric": ["Performance Score"],
        "Score":  [data["overall_performance_score"]]
    })
    fig4 = px.bar(score_df, x="Metric", y="Score",
                  color="Metric", text="Score",
                  color_discrete_sequence=["#e94560"])
    fig4.update_layout(
        dark_chart_layout(""), showlegend=False, height=200
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ═════════════════════════════════════════════════════════
    # ML PERFORMANCE SCORE PREDICTION
    # ═════════════════════════════════════════════════════════
    if res_score.status_code == 200:
        sd = res_score.json()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">📈 ML Performance Score Prediction</div>',
            unsafe_allow_html=True
        )

        # ── Row 4: Score card + Gauge + Grade ─────────────────
        col_s, col_g, col_gr = st.columns([1, 2, 1])

        with col_s:
            st.markdown(f"""
            <div class="card" style="height:220px; display:flex; flex-direction:column;
                                     justify-content:center; align-items:center;">
                <div class="card-label">Predicted Score</div>
                <div style="font-size:52px; font-weight:800;
                            color:{sd['grade_color']}; margin:8px 0;">
                    {sd['predicted_score']}
                </div>
                <div style="font-size:12px; color:#888;">out of 100</div>
                <div style="margin-top:8px; font-size:11px; color:#aaa;">
                    Model: {sd['model_used']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_g:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sd["predicted_score"],
                number={"font": {"color": "#ffffff", "size": 36}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#888"},
                    "bar":  {"color": sd["grade_color"]},
                    "bgcolor":     "#1a1a2e",
                    "bordercolor": "#2a2a4a",
                    "steps": [
                        {"range": [0,  60],  "color": "rgba(231,76,60,0.15)"},
                        {"range": [60, 75],  "color": "rgba(230,126,34,0.15)"},
                        {"range": [75, 85],  "color": "rgba(243,156,18,0.15)"},
                        {"range": [85, 100], "color": "rgba(46,204,113,0.15)"},
                    ],
                    "threshold": {
                        "line":      {"color": sd["grade_color"], "width": 3},
                        "thickness": 0.75,
                        "value":     sd["predicted_score"]
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#1a1a2e",
                font=dict(color="#ccc"),
                margin=dict(l=20, r=20, t=20, b=10),
                height=220
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_gr:
            st.markdown(f"""
            <div class="card" style="height:220px; display:flex; flex-direction:column;
                                     justify-content:center; align-items:center;">
                <div class="card-label">Grade</div>
                <div style="font-size:64px; font-weight:900;
                            color:{sd['grade_color']}; margin:8px 0;">
                    {sd['grade']}
                </div>
                <div style="font-size:11px; color:#aaa;">Performance Grade</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── Row 5: Features (2-col grid) + Radar + Contribution ──
        col_f, col_r, col_c = st.columns([1, 2, 1])

        with col_f:
            st.markdown('<div class="section-title">Input Features</div>',
                        unsafe_allow_html=True)
            feats = sd["input_features"]
            fa, fb = st.columns(2)
            fa.metric("Attendance",  f"{feats['attendance']}%")
            fb.metric("Completion",  f"{feats['completion']}%")
            fc, fd = st.columns(2)
            fc.metric("Projects",    feats["projects"])
            fd.metric("Avg Hours",   f"{feats['hours']}h")
            fe, ff = st.columns(2)
            fe.metric("Late",        feats["late_arrivals"])
            ff.metric("Model", sd["model_used"].split()[0])

        with col_r:
            st.markdown('<div class="section-title">Feature Radar</div>',
                        unsafe_allow_html=True)
            feats = sd["input_features"]
            radar_vals = [
                feats["attendance"],
                feats["completion"],
                min(feats["projects"] * 10, 100),
                min(feats["hours"] * 8, 100),
                max(100 - feats["late_arrivals"] * 7, 0)
            ]
            radar_labels = ["Attendance", "Completion", "Projects", "Hours", "Punctuality"]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                line_color=sd["grade_color"],
                fillcolor="rgba(233,69,96,0.2)"
            ))
            fig_radar.update_layout(
                dark_chart_layout(""),
                polar=dict(
                    bgcolor="#1a1a2e",
                    radialaxis=dict(visible=True, range=[0, 100], color="#888"),
                    angularaxis=dict(color="#888")
                ),
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=10, b=10)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_c:
            st.markdown('<div class="section-title">Contribution</div>',
                        unsafe_allow_html=True)
            for key, val in sd["feature_contribution"].items():
                st.markdown(f"""
                <div style="background:#16213e; border:1px solid #2a2a4a;
                            border-radius:8px; padding:8px 12px;
                            margin-bottom:6px; font-size:12px;">
                    <span style="color:#aaa; font-size:11px;">{key}</span><br>
                    <span style="font-size:13px;">{val}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── Row 6: Threshold bar (full width, compact) ────────
        st.markdown('<div class="section-title">Score vs Grade Thresholds</div>',
                    unsafe_allow_html=True)
        threshold_df = pd.DataFrame({
            "Grade": ["D (0-60)","C (60-70)","B (70-80)",
                      "A (80-90)","A+ (90-100)","Your Score"],
            "Score": [60, 70, 80, 90, 100, sd["predicted_score"]],
            "Type":  ["Threshold","Threshold","Threshold",
                      "Threshold","Threshold","Predicted"]
        })
        fig_bar = px.bar(
            threshold_df, x="Grade", y="Score",
            color="Type", text="Score",
            color_discrete_map={
                "Threshold": "#2a2a4a",
                "Predicted": sd["grade_color"]
            }
        )
        fig_bar.update_layout(
            dark_chart_layout(""),
            showlegend=False,
            height=220
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("ML model not available — run `python ml/train_score_model.py` first.")