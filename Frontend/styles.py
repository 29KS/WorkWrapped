def load_css():
    return """
<style>
    /* ── Base ── */
    .main { background-color: #0f0f0f; }
    .block-container { padding: 1rem 1.5rem; max-width: 100%; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d1a 0%, #0f0f1f 100%);
        border-right: 1px solid #1e1e3a;
        min-width: 220px !important;
        max-width: 220px !important;
    }
    [data-testid="stSidebar"] > div { padding: 0; }

    /* ── Nav buttons ── */
    .nav-btn {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 16px; border-radius: 10px;
        font-size: 13px; color: #888; cursor: pointer;
        transition: all 0.2s; margin: 2px 8px;
        border: 1px solid transparent;
        text-decoration: none;
    }
    .nav-btn:hover {
        background: #1a1a2e; color: #fff;
        border-color: #2a2a4a;
    }
    .nav-btn.active {
        background: linear-gradient(135deg, #e9456015, #e9456025);
        color: #e94560; border-color: #e9456040;
        font-weight: 600;
    }
    .nav-icon { font-size: 16px; min-width: 20px; text-align: center; }
    .nav-label { font-size: 13px; }

    /* ── Nav section label ── */
    .nav-section {
        font-size: 9px; color: #333; letter-spacing: 2px;
        text-transform: uppercase; padding: 12px 24px 4px;
        font-weight: 700;
    }

    /* ── Cards ── */
    .card {
        background: #1a1a2e; border-radius: 12px;
        padding: 16px 20px; text-align: center;
        border: 1px solid #2a2a4a;
    }
    .card-value { font-size: 26px; font-weight: 700; color: #fff; margin: 4px 0; }
    .card-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }

    /* ── Section title ── */
    .section-title {
        font-size: 11px; font-weight: 700; color: #666;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 14px 0 8px 0;
        border-left: 3px solid #e94560; padding-left: 8px;
    }

    /* ── Badges / tags ── */
    .badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .skill-tag {
        display: inline-block; background: #16213e; color: #a0c4ff;
        border: 1px solid #2a2a6a; border-radius: 20px;
        padding: 2px 10px; font-size: 11px; margin: 2px;
    }

    /* ── Page title ── */
    .page-title { font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 2px; }

    /* ── Divider ── */
    .divider { border: none; border-top: 1px solid #1e1e3a; margin: 10px 0; }

    /* ── Achievement card ── */
    .ach-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px; padding: 16px; text-align: center;
        color: white; border: 1px solid #2a2a4a; height: 100%;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #1a1a2e; border: 1px solid #2a2a4a;
        border-radius: 10px; padding: 10px;
    }
    [data-testid="stMetricLabel"] { color: #666 !important; font-size: 10px !important; }
    [data-testid="stMetricValue"] { color: #fff !important; font-size: 18px !important; }

    /* ── Streamlit overrides ── */
    .stButton button {
        background: #1a1a2e; border: 1px solid #2a2a4a;
        color: #ccc; border-radius: 8px;
    }
    .stButton button:hover { border-color: #e94560; color: #fff; }
    [data-testid="stTextInput"] input {
        background: #1a1a2e; border: 1px solid #2a2a4a;
        color: #fff; border-radius: 8px;
    }
    .stDataFrame { background: #1a1a2e; }
    .stProgress > div > div { background: #e94560; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
</style>
"""


def dark_chart_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(color="#888", size=12)),
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font=dict(color="#cccccc", size=11),
        margin=dict(l=20, r=20, t=35, b=20),
        legend=dict(bgcolor="#1a1a2e", bordercolor="#2a2a4a")
    )