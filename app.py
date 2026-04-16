
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page Config (MUST be first Streamlit call) ─────────────────
st.set_page_config(
    page_title="Vaani AI — Voice for Everyone",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/vaani-ai",
        "Report a bug": None,
        "About": "Vaani AI — Voice AI for Accessibility & Societal Impact | Powered by Vapi + Qdrant",
    },
)

# 🔴 Hide Streamlit default multipage sidebar
hide_default_sidebar = """
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_default_sidebar, unsafe_allow_html=True)

# ── Init managers (cached for performance) ────────────────────
@st.cache_resource(show_spinner="Initializing Vaani AI...")
def get_managers():
    from utils.vapi_manager import VapiManager
    from utils.qdrant_manager import VaaniQdrantManager
    vapi = VapiManager()
    qdrant = VaaniQdrantManager()
    return vapi, qdrant


# ── Inject CSS & render nav ───────────────────────────────────
from components.ui import inject_css, render_sidebar_nav
inject_css()
render_sidebar_nav()

# ── Load managers ─────────────────────────────────────────────
vapi_mgr, qdrant_mgr = get_managers()

# ── Route to page ─────────────────────────────────────────────
page = st.session_state.get("current_page", "Home")

if page == "Home":
    from pages.home import render_home
    render_home(vapi_mgr, qdrant_mgr)

elif page == "Voice Assistant":
    from pages.voice_assistant import render_voice_assistant
    render_voice_assistant(vapi_mgr, qdrant_mgr)

elif page == "Chat Interface":
    from pages.chat import render_chat
    render_chat(vapi_mgr, qdrant_mgr)

elif page == "Phone Outreach":
    from pages.phone_outreach import render_phone_outreach
    render_phone_outreach(vapi_mgr, qdrant_mgr)

elif page == "Knowledge Base":
    from pages.knowledge_base import render_knowledge_base
    render_knowledge_base(vapi_mgr, qdrant_mgr)

elif page == "Analytics":
    from pages.analytics import render_analytics
    render_analytics(vapi_mgr, qdrant_mgr)

elif page == "Settings":
    from pages.settings import render_settings
    render_settings(vapi_mgr, qdrant_mgr)
