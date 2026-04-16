"""
Vaani AI - Shared UI Components & Styling
"""
import streamlit as st
from config import APP_NAME, THEME


GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
}

.main { background: #F8F9FA; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1100px !important; }

/* ── Hide Streamlit chrome ─────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Typography ────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #202124;
    font-weight: 700;
}

/* ── Cards ─────────────────────────────────────── */
.card {
    background: #fff;
    border-radius: 12px;
    border: 1px solid #DADCE0;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

/* ── Status Badges ──────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.badge-green { background: #E8F5E9; color: #2E7D32; }
.badge-blue  { background: #E3F2FD; color: #1565C0; }
.badge-orange{ background: #FFF3E0; color: #E65100; }
.badge-red   { background: #FFEBEE; color: #C62828; }
.badge-grey  { background: #F1F3F4; color: #5F6368; }

/* ── Top Banner ─────────────────────────────────── */
.top-banner {
    background: linear-gradient(135deg, #1A73E8 0%, #0D47A1 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.top-banner h2 { color: white; margin: 0; font-size: 1.3rem; }
.top-banner p  { color: rgba(255,255,255,0.85); margin: 0.2rem 0 0; font-size: 0.85rem; }

/* ── Metric Cards ───────────────────────────────── */
.metric-card {
    background: white;
    border-radius: 10px;
    border: 1px solid #DADCE0;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-val {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1A73E8;
}
.metric-label {
    font-size: 0.78rem;
    color: #5F6368;
    margin-top: 2px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Domain Cards ───────────────────────────────── */
.domain-card {
    background: white;
    border-radius: 12px;
    border: 2px solid #DADCE0;
    padding: 1.1rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
    height: 100%;
}
.domain-card:hover {
    border-color: #1A73E8;
    box-shadow: 0 2px 10px rgba(26,115,232,0.15);
    transform: translateY(-2px);
}
.domain-card.selected {
    border-color: #1A73E8;
    background: #E8F0FE;
}
.domain-card .icon { font-size: 2rem; margin-bottom: 0.4rem; }
.domain-card .title { font-weight: 600; font-size: 0.9rem; color: #202124; }
.domain-card .desc  { font-size: 0.75rem; color: #5F6368; margin-top: 2px; }

/* ── Voice Button ───────────────────────────────── */
.voice-btn-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1.5rem 0;
}
.voice-ring {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1A73E8, #0D47A1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    box-shadow: 0 0 0 0 rgba(26,115,232,0.4);
    animation: pulse 2s infinite;
    cursor: pointer;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(26,115,232,0.4); }
    70%  { box-shadow: 0 0 0 18px rgba(26,115,232,0); }
    100% { box-shadow: 0 0 0 0 rgba(26,115,232,0); }
}
.voice-ring.active {
    background: linear-gradient(135deg, #34A853, #1B5E20);
    animation: pulse-green 1s infinite;
}
@keyframes pulse-green {
    0%   { box-shadow: 0 0 0 0 rgba(52,168,83,0.4); }
    70%  { box-shadow: 0 0 0 18px rgba(52,168,83,0); }
    100% { box-shadow: 0 0 0 0 rgba(52,168,83,0); }
}

/* ── Chat Bubbles ───────────────────────────────── */
.chat-msg {
    margin: 0.5rem 0;
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
}
.chat-msg.user { flex-direction: row-reverse; }
.chat-bubble {
    max-width: 75%;
    padding: 0.65rem 1rem;
    border-radius: 14px;
    font-size: 0.88rem;
    line-height: 1.45;
}
.chat-bubble.user {
    background: #1A73E8;
    color: white;
    border-bottom-right-radius: 4px;
}
.chat-bubble.ai {
    background: white;
    color: #202124;
    border: 1px solid #DADCE0;
    border-bottom-left-radius: 4px;
}

/* ── Table Styling ──────────────────────────────── */
.vaani-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.vaani-table th {
    background: #F8F9FA;
    border-bottom: 2px solid #DADCE0;
    padding: 0.6rem 0.8rem;
    text-align: left;
    font-weight: 600;
    color: #5F6368;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.5px;
}
.vaani-table td {
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid #F1F3F4;
    color: #202124;
}
.vaani-table tr:hover td { background: #F8F9FA; }

/* ── Info Boxes ─────────────────────────────────── */
.info-box {
    background: #E8F0FE;
    border-left: 4px solid #1A73E8;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #1A237E;
    margin: 0.5rem 0;
}
.warn-box {
    background: #FFF8E1;
    border-left: 4px solid #FBBC04;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #5D4037;
    margin: 0.5rem 0;
}
.success-box {
    background: #E8F5E9;
    border-left: 4px solid #34A853;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #1B5E20;
    margin: 0.5rem 0;
}

/* ── Nav Pills ──────────────────────────────────── */
.nav-pills { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.nav-pill {
    padding: 0.35rem 0.8rem;
    border-radius: 99px;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid #DADCE0;
    background: white;
    color: #5F6368;
    transition: all 0.15s;
}
.nav-pill:hover, .nav-pill.active {
    background: #1A73E8;
    color: white;
    border-color: #1A73E8;
}

/* ── Sidebar Tweaks ─────────────────────────────── */
.css-1d391kg, section[data-testid="stSidebar"] {
    background: #fff !important;
    border-right: 1px solid #DADCE0 !important;
}

/* ── Streamlit Overrides ────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(0,0,0,0.12);
}
.stSelectbox > div, .stTextInput > div > div {
    border-radius: 8px !important;
}
.stExpander > details {
    border-radius: 8px !important;
    border: 1px solid #DADCE0 !important;
}

/* ── Footer ─────────────────────────────────────── */
.vaani-footer {
    text-align: center;
    padding: 1.5rem;
    margin-top: 2rem;
    border-top: 1px solid #DADCE0;
    color: #5F6368;
    font-size: 0.8rem;
}
</style>
"""


def inject_css():
    """Inject global CSS into the Streamlit app."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_top_banner(title: str, subtitle: str, icon: str = "🎙️"):
    st.markdown(f"""
    <div class="top-banner">
        <div style="font-size:2.2rem">{icon}</div>
        <div>
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric(value, label: str, delta: str = ""):
    delta_html = f'<div style="color:#34A853;font-size:0.75rem;margin-top:2px">↑ {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, color: str = "blue"):
    st.markdown(f'<span class="badge badge-{color}">{text}</span>', unsafe_allow_html=True)


def render_info(text: str):
    st.markdown(f'<div class="info-box">ℹ️ {text}</div>', unsafe_allow_html=True)


def render_warn(text: str):
    st.markdown(f'<div class="warn-box">⚠️ {text}</div>', unsafe_allow_html=True)


def render_success(text: str):
    st.markdown(f'<div class="success-box">✅ {text}</div>', unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="vaani-footer">
        <strong>Vaani AI</strong> — Voice AI for Accessibility & Societal Impact<br>
        Powered by <strong>Vapi</strong> (Voice AI) · <strong>Qdrant</strong> (Vector Search) · Built with ❤️ for inclusive India
    </div>
    """, unsafe_allow_html=True)


def status_indicator(connected: bool, label: str) -> str:
    if connected:
        return f'<span class="badge badge-green">🟢 {label} Connected</span>'
    else:
        return f'<span class="badge badge-orange">🟡 {label} Demo Mode</span>'


def render_sidebar_nav():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 1.5rem">
            <div style="font-size:2.5rem">🎙️</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:1.3rem;color:#202124">Vaani AI</div>
            <div style="font-size:0.75rem;color:#5F6368;margin-top:2px">Voice for Everyone</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        pages = {
            "🏠 Home": "Home",
            "🎙️ Voice Assistant": "Voice Assistant",
            "💬 Chat Interface": "Chat Interface",
            "📞 Phone Outreach": "Phone Outreach",
            "🧠 Knowledge Base": "Knowledge Base",
            "📊 Analytics": "Analytics",
            "⚙️ Settings": "Settings",
        }

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"

        for icon_label, page in pages.items():
            is_active = st.session_state.current_page == page
            if st.button(
                icon_label,
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.75rem;color:#5F6368;padding:0 0.5rem">
            <strong>Version</strong> 1.0.0<br>
            <strong>Stack</strong> Vapi · Qdrant · Streamlit<br><br>
            <em>Breaking barriers through voice</em>
        </div>
        """, unsafe_allow_html=True)
