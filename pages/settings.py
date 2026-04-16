"""
Vaani AI - Settings Page
API configuration, user preferences, system management
"""
import streamlit as st
from components.ui import render_top_banner, render_success, render_warn, render_info, render_footer


def render_settings(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Settings",
        "Configure API keys, preferences, and system parameters",
        "⚙️",
    )

    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "🎛️ Preferences", "🔧 System"])

    # ── Tab 1: API Keys ───────────────────────────────────────
    with tab1:
        st.markdown("#### Vapi Configuration")
        render_info("Get your API keys from vapi.ai — Required for live voice calls")

        with st.form("vapi_config"):
            vapi_key = st.text_input(
                "Vapi API Key",
                value=st.session_state.get("vapi_api_key", ""),
                type="password",
                placeholder="va-xxxxxxxxxxxxxxxxxxxxxxxx",
            )
            vapi_asst = st.text_input(
                "Default Assistant ID (optional)",
                value=st.session_state.get("vapi_assistant_id", ""),
                placeholder="Leave blank to auto-create assistants",
            )
            vapi_phone = st.text_input(
                "Phone Number ID (for outbound calls)",
                value=st.session_state.get("vapi_phone_id", ""),
                placeholder="Your Vapi phone number ID",
            )
            if st.form_submit_button("💾 Save Vapi Settings", type="primary"):
                st.session_state.vapi_api_key = vapi_key
                st.session_state.vapi_assistant_id = vapi_asst
                st.session_state.vapi_phone_id = vapi_phone
                render_success("Vapi settings saved! Restart app to apply.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Qdrant Configuration")
        render_info("Connect to Qdrant Cloud or self-hosted instance for persistent vector storage")

        with st.form("qdrant_config"):
            q_url = st.text_input(
                "Qdrant URL",
                value=st.session_state.get("qdrant_url", "http://localhost:6333"),
                placeholder="https://your-cluster.qdrant.io",
            )
            q_key = st.text_input(
                "Qdrant API Key (for cloud)",
                value=st.session_state.get("qdrant_api_key", ""),
                type="password",
                placeholder="Leave blank for local",
            )
            if st.form_submit_button("💾 Save Qdrant Settings", type="primary"):
                st.session_state.qdrant_url = q_url
                st.session_state.qdrant_api_key = q_key
                render_success("Qdrant settings saved! Restart app to reconnect.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### OpenAI Configuration")
        render_info("Optional — Used for enhanced AI responses in Chat Interface. Vapi handles voice AI independently.")

        with st.form("openai_config"):
            oai_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.get("openai_key", ""),
                type="password",
                placeholder="sk-xxxxxxxxxxxxxxxx",
            )
            if st.form_submit_button("💾 Save OpenAI Key", type="primary"):
                st.session_state.openai_key = oai_key
                render_success("OpenAI key saved!")

    # ── Tab 2: Preferences ────────────────────────────────────
    with tab2:
        st.markdown("#### User Preferences")

        col1, col2 = st.columns(2)
        with col1:
            from config import LANGUAGES
            default_lang = st.selectbox(
                "Default Language",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: f"{LANGUAGES[x]['flag']} {LANGUAGES[x]['name']}",
                index=0,
            )

            from config import SERVICE_DOMAINS
            default_domain = st.selectbox(
                "Default Domain",
                options=list(SERVICE_DOMAINS.keys()),
                format_func=lambda x: f"{SERVICE_DOMAINS[x]['icon']} {SERVICE_DOMAINS[x]['title']}",
            )

            literacy_level = st.select_slider(
                "Language Complexity",
                options=["Very Simple", "Simple", "Standard", "Detailed"],
                value="Simple",
                help="Controls how complex Vaani's responses are",
            )

        with col2:
            enable_personalization = st.toggle("Enable Personalization (Qdrant History)", value=True)
            enable_recording = st.toggle("Allow Call Recording", value=False)
            enable_analytics = st.toggle("Share Anonymous Analytics", value=True)
            auto_language_detect = st.toggle("Auto-detect Language", value=True)

        voice_speed = st.slider("Voice Speed", 0.5, 2.0, 1.0, 0.1, format="%.1fx")
        voice_options = ["Natural Female", "Natural Male", "Clear Female", "Clear Male"]
        voice_style = st.selectbox("Voice Style", voice_options)

        if st.button("💾 Save Preferences", type="primary"):
            st.session_state.user_prefs = {
                "language": default_lang,
                "domain": default_domain,
                "literacy_level": literacy_level,
                "personalization": enable_personalization,
                "recording": enable_recording,
                "analytics": enable_analytics,
                "auto_language": auto_language_detect,
                "voice_speed": voice_speed,
                "voice_style": voice_style,
            }
            render_success("Preferences saved successfully!")

    # ── Tab 3: System ─────────────────────────────────────────
    with tab3:
        st.markdown("#### 🔧 System Status")

        vapi_status = vapi_mgr.get_status()
        qdrant_status = qdrant_mgr.get_status()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Vapi**")
            st.json({
                "connected": vapi_status["connected"],
                "mode": vapi_status["mode"],
                "assistant": vapi_status.get("assistant_id", "not_configured"),
            })
        with col2:
            st.markdown("**Qdrant**")
            st.json({
                "connected": qdrant_status["connected"],
                "mode": qdrant_status["mode"],
                "url": qdrant_status.get("url", ""),
            })

        st.markdown("---")
        st.markdown("#### 🗑️ Data Management")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🗑️ Clear Session Data", use_container_width=True):
                for key in ["chat_messages", "call_history", "call_log", "last_transcript"]:
                    if key in st.session_state:
                        del st.session_state[key]
                render_success("Session data cleared")

        with col_b:
            if st.button("📤 Export Interactions", use_container_width=True):
                import json
                export_data = {
                    "chat": st.session_state.get("chat_messages", []),
                    "calls": st.session_state.get("call_history", []),
                }
                st.download_button(
                    "⬇️ Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name="vaani_export.json",
                    mime="application/json",
                )

        with col_c:
            if st.button("🔄 Reset All", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 Setup Guide")
        st.markdown("""
        <div class="card">
            <div style="font-weight:600;margin-bottom:0.75rem">🚀 Quick Setup (5 minutes)</div>
            
            <div style="margin-bottom:0.5rem">
                <span class="badge badge-blue">Step 1</span>
                <strong style="margin-left:0.5rem">Qdrant</strong> — 
                Run <code>docker run -p 6333:6333 qdrant/qdrant</code> or sign up at <a href="https://cloud.qdrant.io" target="_blank">cloud.qdrant.io</a>
            </div>
            <div style="margin-bottom:0.5rem">
                <span class="badge badge-blue">Step 2</span>
                <strong style="margin-left:0.5rem">Vapi</strong> — 
                Sign up at <a href="https://vapi.ai" target="_blank">vapi.ai</a>, create a phone number, get your API key
            </div>
            <div style="margin-bottom:0.5rem">
                <span class="badge badge-blue">Step 3</span>
                <strong style="margin-left:0.5rem">Configure</strong> — 
                Add keys above or in <code>.env</code> file
            </div>
            <div style="margin-bottom:0.5rem">
                <span class="badge badge-blue">Step 4</span>
                <strong style="margin-left:0.5rem">Seed</strong> — 
                Go to Knowledge Base → "Seed Default KB"
            </div>
            <div>
                <span class="badge badge-green">Ready!</span>
                <strong style="margin-left:0.5rem">Test</strong> — 
                Navigate to Voice Assistant and start a call
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_footer()
