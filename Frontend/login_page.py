import streamlit as st
import requests
from Frontend.styles import load_css

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="EffiTrack – Login", layout="centered")
st.markdown(load_css(), unsafe_allow_html=True)

# redirect if already logged in
if st.session_state.get("token"):
    st.success(f"Already logged in as {st.session_state.get('email')}")
    st.stop()

st.markdown("""
<div style="text-align:center; padding: 40px 0 20px 0;">
    <div style="font-size:36px;">⚡</div>
    <div style="font-size:28px; font-weight:800; color:#ffffff;">EffiTrack</div>
    <div style="font-size:13px; color:#888; margin-top:4px;">
        AI-Powered Employee Performance Analytics
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#1a1a2e; border:1px solid #2a2a4a;
            border-radius:16px; padding:32px; max-width:420px; margin:auto;">
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Login to your account</div>',
            unsafe_allow_html=True)

email    = st.text_input("Email", placeholder="your@email.com")
password = st.text_input("Password", type="password", placeholder="Password")

if st.button("Login", type="primary", use_container_width=True):
    if not email or not password:
        st.error("Please enter both email and password")
    else:
        res = requests.post(f"{API_BASE}/auth/login",
                            json={"email": email, "password": password})
        if res.status_code == 200:
            data = res.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["uid"]   = data["uid"]
            st.session_state["role"]  = data["role"]
            st.session_state["email"] = data["email"]
            st.success("Login successful!")
            st.info(f"Your UID: `{data['uid']}`")
            st.info(f"Default password is the part of your email before @  "
                    f"e.g. `mahakkanwar0`")
        else:
            st.error("Invalid email or password")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-top:16px; font-size:12px; color:#555;">
    Contact your admin if you don't have access
</div>
""", unsafe_allow_html=True)