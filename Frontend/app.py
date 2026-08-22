import streamlit as st
import requests
from styles import load_css

API_BASE = "https://workwrapped-backend.onrender.com/"

st.set_page_config(
    page_title="WorkWrapped",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS (injected once, top of script — prevents flicker) ──
st.markdown(load_css(), unsafe_allow_html=True)

st.markdown("""
<style>
    /* Hide Streamlit's auto-generated multipage nav list (we build our own),
       but DO NOT hide collapsedControl — that's the arrow that lets users
       re-open the sidebar. Hiding it is what was breaking your nav bar. */
    # [data-testid="stSidebarNav"] { display: none !important; }
    # [data-testid="stSidebarNavItems"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* Force the sidebar to always render at a sane width when expanded */
    [data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
    }

    /* Make the sidebar's inner content a flex column so we can pin
       the logout button to the bottom without a spacer hack */
    [data-testid="stSidebarContent"] {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        padding-bottom: 0 !important;
    }

    .nav-scroll-area {
        flex: 1 1 auto;
        overflow-y: auto;
    }

    .sticky-logout {
        flex-shrink: 0;
        padding: 10px 8px 16px;
        background: #0f0f1e;
        border-top: 1px solid #1e1e3a;
    }

    .nav-section {
        font-size: 10px;
        letter-spacing: 1.5px;
        color: #555;
        font-weight: 700;
        margin: 18px 8px 6px;
    }

    /* Colored left-accent + background for the active nav button.
       Targets the primary-type button Streamlit renders for the active page. */
    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: linear-gradient(90deg, rgba(233,69,96,0.18), rgba(15,52,96,0.05)) !important;
        border-left: 3px solid #e94560 !important;
        color: #fff !important;
        font-weight: 700 !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        color: #9a9ab0 !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
        background: #13132a !important;
        color: #fff !important;
    }
    [data-testid="stSidebar"] .stButton button {
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-bottom: 2px !important;
        transition: background 0.15s ease, color 0.15s ease;
    }
</style>
""", unsafe_allow_html=True)


# ── colored icon accents per nav key (used for the little dot before label) ──
ICON_COLORS = {
    "dashboard":       "#e94560",
    "profile":         "#4f8cff",
    "work_statistics": "#f2a900",
    "productivity":    "#22c55e",
    "attendance":      "#a855f7",
    "performance":     "#06b6d4",
    "achievements":    "#f59e0b",
    "projects":        "#3b82f6",
    "burnout":         "#ef4444",
    "wrapped":         "#e94560",
}


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()


def restore_session_from_query_params():
    """Persist login across a hard browser refresh.

    st.session_state is wiped on a full page reload, but the URL's query
    string survives. We mirror the auth info into st.query_params on login,
    and on every fresh script start (before session_state is populated) we
    rehydrate session_state from it.
    """
    if st.session_state.get("token"):
        return  # already have a live session, nothing to restore

    qp = st.query_params
    if qp.get("token") and qp.get("uid") and qp.get("email") and qp.get("role"):
        st.session_state.update({
            "token": qp.get("token"),
            "uid":   qp.get("uid"),
            "email": qp.get("email"),
            "role":  qp.get("role"),
            "page":  qp.get("page", "dashboard"),
        })


def render_sidebar(uid):
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 16px 12px; border-bottom:1px solid #1e1e3a;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:linear-gradient(135deg,#e94560,#0f3460);
                            border-radius:10px; width:36px; height:36px;
                            display:flex; align-items:center; justify-content:center;
                            font-size:18px; font-weight:900; color:#fff;">⚡</div>
                <div>
                    <div style="font-size:16px; font-weight:900; color:#fff;">WorkWrapped</div>
                    <div style="font-size:9px; color:#444; letter-spacing:1px;">
                        PERFORMANCE ANALYTICS
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        email   = st.session_state.get("email", "")
        name    = email.split("@")[0].replace(".", " ").title()
        role    = st.session_state.get("role", "intern").title()
        initial = email[0].upper() if email else "?"

        st.markdown(f"""
        <div style="margin:12px 8px; padding:12px; background:#13132a;
                    border-radius:10px; border:1px solid #1e1e3a;
                    display:flex; align-items:center; gap:10px;">
            <div style="background:linear-gradient(135deg,#e94560,#0f3460);
                        border-radius:50%; width:36px; height:36px; min-width:36px;
                        display:flex; align-items:center; justify-content:center;
                        font-size:15px; color:#fff; font-weight:800;">{initial}</div>
            <div style="overflow:hidden;">
                <div style="font-size:13px; color:#fff; font-weight:600;
                            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    {name}
                </div>
                <div style="font-size:10px; color:#555;">{role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        current = st.session_state.get("page", "dashboard")

        nav_groups = {
            "MAIN": [
                ("🏠", "Dashboard",       "dashboard"),
                ("👤", "My Profile",      "profile"),
            ],
            "ANALYTICS": [
                ("📊", "Work Statistics", "work_statistics"),
                ("⚡", "Productivity",    "productivity"),
                ("🗓️", "Attendance",      "attendance"),
                ("🎯", "Performance",     "performance"),
            ],
            "INSIGHTS": [
                ("🏆", "Achievements",    "achievements"),
                ("📁", "Projects",        "projects"),
                ("🔥", "Burnout Risk",    "burnout"),
            ],
            "REPORT": [
                ("✨", "My Wrapped",      "wrapped"),
            ]
        }

        # scrollable nav area (everything except the logout button)
        st.markdown('<div class="nav-scroll-area">', unsafe_allow_html=True)

        for group, items in nav_groups.items():
            st.markdown(f"<div class='nav-section'>{group}</div>", unsafe_allow_html=True)

            for icon, label, key in items:
                active = current == key
                dot_color = ICON_COLORS.get(key, "#e94560")

                # colored dot rendered just above the button so the icon
                # region visually carries the accent color
                st.markdown(
                    f"""<div style="display:flex; align-items:center; gap:6px;
                                margin:2px 8px -30px 10px; position:relative; z-index:2;
                                pointer-events:none;">
                            <span style="width:6px; height:6px; border-radius:50%;
                                        background:{dot_color if active else 'transparent'};
                                        display:inline-block;"></span>
                        </div>""",
                    unsafe_allow_html=True
                )

                if st.button(
                    f"{icon}  {label}",
                    key=f"btn_{key}",
                    use_container_width=True,
                    type="primary" if active else "secondary"
                ):
                    st.session_state["page"] = key
                    # keep query params in sync so a refresh lands on the same page
                    st.query_params.update({"page": key})
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # end nav-scroll-area

        # ── sticky logout, pinned via flex layout (not a spacer hack) ──
        st.markdown('<div class="sticky-logout">', unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)


def show_login():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        .block-container { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    col = st.columns([1, 1.2, 1])[1]
    with col:
        st.markdown("""
        <div style="text-align:center; padding:60px 0 32px;">
            <div style="font-size:56px;">⚡</div>
            <div style="font-size:30px; font-weight:900; color:#fff; margin-top:8px;">
                WorkWrapped
            </div>
            <div style="font-size:13px; color:#555; margin-top:6px;">
                AI-Powered Employee Performance Analytics
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#1a1a2e; border:1px solid #2a2a4a;
                    border-radius:16px; padding:28px 28px 8px;
                    margin-bottom:4px;">
            <div style="font-size:17px; font-weight:700; color:#fff; margin-bottom:16px;">
                Welcome back 👋
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password",
                                     placeholder="Enter your password")
            submitted = st.form_submit_button(
                "Login →", use_container_width=True, type="primary"
            )

        if submitted:
            if not email or not password:
                st.error("Please fill in both fields")
            else:
                with st.spinner("Authenticating..."):
                    res = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"email": email, "password": password}
                    )
                if res.status_code == 200:
                    d = res.json()
                    st.session_state.update({
                        "token": d["access_token"],
                        "uid":   d["uid"],
                        "role":  d["role"],
                        "email": d["email"],
                        "page":  "dashboard"
                    })
                    # mirror into the URL so a hard refresh doesn't log you out
                    st.query_params.update({
                        "token": d["access_token"],
                        "uid":   str(d["uid"]),
                        "role":  d["role"],
                        "email": d["email"],
                        "page":  "dashboard",
                    })
                    st.rerun()
                else:
                    st.error("Invalid email or password")


def main():
    restore_session_from_query_params()

    if not st.session_state.get("token"):
        show_login()
        return

    uid  = st.session_state["uid"]
    page = st.session_state.get("page", "dashboard")

    render_sidebar(uid)

    if page == "dashboard":
        from pages.dashboard import show
    elif page == "profile":
        from pages.employee_page import show
    elif page == "work_statistics":
        from pages.work_statistics_page import show
    elif page == "productivity":
        from pages.productivity_page import show
    elif page == "attendance":
        from pages.attendance_page import show
    elif page == "performance":
        from pages.performance_page import show
    elif page == "achievements":
        from pages.achievement_page import show
    elif page == "projects":
        from pages.projects_page import show
    elif page == "burnout":
        from pages.burnout_page import show
    elif page == "wrapped":
        from pages.wrapped_page import show
    else:
        from pages.dashboard import show

    show(uid)


if __name__ == "__main__":
    main()