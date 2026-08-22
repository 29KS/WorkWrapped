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
    res = requests.get(f"{API_BASE}/employees/{uid}")
    if res.status_code != 200:
        return None
    return res.json()

def show(uid):
    st.markdown('<div class="page-title">👤 Employee Profile</div>', unsafe_allow_html=True)

    res = requests.get(f"{API_BASE}/employees/{uid}")
    if res.status_code != 200:
        st.error("Employee not found")
        return

    e = res.json()
    status = e.get("status", "Unknown")
    status_color = "#2ecc71" if status == "Active" else "#e74c3c"

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 1: Avatar + Contact + KPIs ───────────────────────
    col_avatar, col_info, col_kpi = st.columns([1, 2, 3])

    with col_avatar:
        st.markdown(f"""
        <div class="card">
            <div style="
                background: linear-gradient(135deg, #e94560, #0f3460);
                border-radius: 50%; width: 64px; height: 64px;
                display: flex; align-items: center; justify-content: center;
                font-size: 26px; color: white; font-weight: bold; margin: auto;
            ">{e.get("email","?")[0].upper()}</div>
            <div style="margin-top:10px; font-size:14px; color:#fff; font-weight:600;">
                {e.get("role","N/A")}
            </div>
            <div style="font-size:12px; color:#aaa;">{e.get("position","N/A")}</div>
            <div style="margin-top:8px;">
                <span class="badge" style="background:{status_color}22; color:{status_color};">
                    {status}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"""
        <div class="card" style="text-align:left; height:100%;">
            <div class="card-label">Contact & Location</div>
            <hr class="divider">
            <div style="font-size:13px; color:#ccc; line-height:2;">
                📧 {e.get("email","N/A")}<br>
                📞 {e.get("phone","N/A")}<br>
                📍 {e.get("address","N/A")}<br>
                🏫 {e.get("college","N/A")}<br>
                🎓 {e.get("branch","N/A")} — {e.get("year","N/A")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi:
        k1, k2, k3 = st.columns(3)
        k1.metric("Department", e.get("department", "N/A"))
        k2.metric("Work Mode", e.get("workMode", "N/A"))
        k3.metric("Internship", e.get("internshipType", "N/A"))

        k4, k5, k6 = st.columns(3)
        k4.metric("Joined", e.get("joinDate", "N/A"))
        k5.metric("Reports To", e.get("reportingTo", "N/A"))
        k6.metric("Assessment", f"{e.get('assessmentScore','N/A')}/100")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Personality Card ──────────────────────────────────────
    res_p = requests.get(f"{API_BASE}/employees/{uid}/personality")
    if res_p.status_code == 200:
        p = res_p.json()
        st.markdown('<div class="section-title">Work Personality</div>',
                    unsafe_allow_html=True)

        pcol1, pcol2, pcol3 = st.columns([1, 2, 2])

        with pcol1:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:52px;">{p['emoji']}</div>
                <div style="font-size:16px; font-weight:800;
                            color:#ffffff; margin-top:8px;">
                    {p['personality']}
                </div>
                <div style="font-size:11px; color:#aaa; margin-top:6px;">
                    Work Personality Type
                </div>
            </div>
            """, unsafe_allow_html=True)

        with pcol2:
            st.markdown(f"""
            <div class="card" style="text-align:left; height:100%;">
                <div class="card-label">About this personality</div>
                <hr class="divider">
                <div style="font-size:14px; color:#ccc; line-height:1.8;">
                    {p['description']}
                </div>
                <hr class="divider">
                <div style="font-size:12px; color:#888;">
                    Based on: {p['input_features']['tasks_completed']} tasks •
                    {p['input_features']['attendance']}% attendance •
                    {p['input_features']['projects']} projects
                </div>
            </div>
            """, unsafe_allow_html=True)

        with pcol3:
            prob = p["probabilities"]
            df_prob = pd.DataFrame({
                "Type": list(prob.keys()),
                "Probability": list(prob.values())
            }).sort_values("Probability", ascending=True)

            fig_p = px.bar(
                df_prob, x="Probability", y="Type",
                orientation="h",
                color="Probability",
                color_continuous_scale="Purples",
                labels={"Probability": "%", "Type": ""},
                text="Probability"
            )
            fig_p.update_layout(
                dark_chart_layout("Personality Match %"),
                height=220,
                margin=dict(l=10, r=10, t=30, b=10),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_p, use_container_width=True)

    # ── Row 2: Skills + Certifications ───────────────────────
    col_skills, col_certs = st.columns([3, 2])

    with col_skills:
        st.markdown('<div class="section-title">Skills</div>', unsafe_allow_html=True)
        skills_html = " ".join([
            f'<span class="skill-tag">{s}</span>'
            for s in e.get("skills", [])
        ])
        st.markdown(skills_html, unsafe_allow_html=True)

    with col_certs:
        st.markdown('<div class="section-title">Certifications</div>', unsafe_allow_html=True)
        for cert in e.get("certifications", []):
            st.markdown(
                f"<div style='font-size:12px; color:#ccc; padding:3px 0;'>✅ {cert}</div>",
                unsafe_allow_html=True
            )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Row 3: Summary + Links ────────────────────────────────
    col_summary, col_links = st.columns([4, 1])

    with col_summary:
        st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#1a1a2e; border-radius:10px; padding:12px;
                    font-size:13px; color:#ccc; border:1px solid #2a2a4a;">
            {e.get("summary","No summary available")}
        </div>
        """, unsafe_allow_html=True)

    with col_links:
        st.markdown('<div class="section-title">Links</div>', unsafe_allow_html=True)
        if e.get("github"):
            st.markdown(f"🐙 [GitHub](https://{e.get('github')})")
        if e.get("linkedin"):
            st.markdown(f"💼 [LinkedIn](https://{e.get('linkedin')})")
        st.markdown(
            f"<div style='font-size:11px; color:#888; margin-top:8px;'>📄 {e.get('offerLetterRef','N/A')}</div>",
            unsafe_allow_html=True
        )