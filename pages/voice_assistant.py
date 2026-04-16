"""
Vaani AI - Voice Assistant Page
Core voice interaction using Vapi
"""
import uuid
import time
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

from config import SERVICE_DOMAINS, LANGUAGES
from components.ui import render_top_banner, render_info, render_warn, render_success, render_footer


def render_voice_assistant(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Voice Assistant",
        "Talk to Vaani — Get help in your language, in your words",
        "🎙️",
    )

    # ── Session Init ──────────────────────────────────────────
    if "voice_session_id" not in st.session_state:
        st.session_state.voice_session_id = str(uuid.uuid4())
    if "call_active" not in st.session_state:
        st.session_state.call_active = False
    if "call_id" not in st.session_state:
        st.session_state.call_id = None
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = None
    if "call_history" not in st.session_state:
        st.session_state.call_history = []

    # ── Config Panel ──────────────────────────────────────────
    col_cfg, col_voice = st.columns([1, 1.4])

    with col_cfg:
        st.markdown("#### ⚙️ Configure Assistant")

        # Domain selection
        st.markdown("**Select Service Domain**")
        domain_icons = {k: f"{v['icon']} {v['title']}" for k, v in SERVICE_DOMAINS.items()}
        selected_domain = st.selectbox(
            "Domain",
            options=list(domain_icons.keys()),
            format_func=lambda x: domain_icons[x],
            key="selected_domain",
            label_visibility="collapsed",
        )

        # Language selection
        st.markdown("**Select Language**")
        lang_options = {k: f"{v['flag']} {v['name']} ({v['native']})" for k, v in LANGUAGES.items()}
        selected_lang = st.selectbox(
            "Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            key="selected_lang",
            label_visibility="collapsed",
        )

        # User ID for personalization
        if "user_id" not in st.session_state:
            st.session_state.user_id = f"user_{str(uuid.uuid4())[:8]}"
        user_id = st.text_input("Your ID (for personalization)", value=st.session_state.user_id, key="uid_input")
        st.session_state.user_id = user_id

        # Domain info
        domain_data = SERVICE_DOMAINS[selected_domain]
        st.markdown(f"""
        <div class="card" style="background:{domain_data['color']};border-color:{domain_data['accent']}33">
            <div style="font-size:1.5rem">{domain_data['icon']}</div>
            <div style="font-weight:600;font-size:0.88rem;color:{domain_data['accent']}">{domain_data['title']}</div>
            <div style="font-size:0.78rem;color:#5F6368;margin-top:2px">{domain_data['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Knowledge retrieval preview
        with st.expander("🔍 Knowledge Preview (Qdrant)"):
            if st.button("Fetch Relevant Info", key="kb_preview"):
                query_preview = f"help with {selected_domain}"
                results = qdrant_mgr.search_knowledge(query_preview, domain=selected_domain, top_k=3)
                if results:
                    for r in results:
                        score_pct = int(r.get("score", 0) * 100)
                        st.markdown(f"""
                        <div style="background:#F8F9FA;border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.5rem;font-size:0.8rem">
                            <div style="color:#1A73E8;font-weight:600;margin-bottom:2px">{score_pct}% match</div>
                            {r['text'][:150]}...
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("*No preview available — knowledge base empty*")

    # ── Voice Panel ───────────────────────────────────────────
    with col_voice:
        st.markdown("#### 🎙️ Start Voice Call")

        vapi_status = vapi_mgr.get_status()
        if not vapi_status["connected"]:
            render_warn("Vapi not connected — running in demo mode. Add your API key in Settings.")

        # Build Vapi Web Call Widget
        vapi_key = st.session_state.get("vapi_api_key", "")

        if not st.session_state.call_active:
            # Start call button
            if st.button("📞 Start Voice Call", type="primary", use_container_width=True, key="start_call"):
                with st.spinner("Connecting to Vaani..."):
                    # Get user context from Qdrant
                    user_ctx = qdrant_mgr.get_user_context(
                        user_id, f"help with {selected_domain}", top_k=2
                    )
                    ctx_text = "\n".join([f"- {u['query']}" for u in user_ctx]) if user_ctx else ""

                    # Get knowledge context
                    kb_results = qdrant_mgr.search_knowledge(
                        f"guide for {selected_domain}", domain=selected_domain, top_k=3
                    )
                    kb_text = "\n".join([r["text"] for r in kb_results])

                    # Create assistant
                    assistant = vapi_mgr.create_domain_assistant(
                        domain=selected_domain,
                        language=selected_lang,
                        user_context=ctx_text,
                        knowledge_context=kb_text,
                    )
                    st.session_state.assistant_id = assistant.get("id")
                    st.session_state.call_active = True
                    st.rerun()

        if st.session_state.call_active:
            # ── Vapi Web SDK Widget ───────────────────────────
            assistant_id = st.session_state.get("assistant_id", "")

            # Inject Vapi web call widget
            vapi_widget_html = f"""
            <div id="vaani-voice-widget" style="text-align:center;padding:1rem">
                <div id="call-status" style="
                    width:100px;height:100px;border-radius:50%;
                    background:linear-gradient(135deg,#34A853,#1B5E20);
                    display:flex;align-items:center;justify-content:center;
                    font-size:2.5rem;margin:0 auto 1rem;
                    box-shadow:0 0 0 0 rgba(52,168,83,0.4);
                    animation:pulse-green 1.2s infinite;
                ">🎙️</div>
                <div id="status-text" style="font-weight:600;color:#34A853;font-size:1rem">● Call Active</div>
                <div id="duration-text" style="color:#5F6368;font-size:0.8rem;margin-top:4px">Duration: <span id="timer">00:00</span></div>
                <div style="margin-top:0.75rem;font-size:0.82rem;color:#5F6368">
                    Domain: <strong>{selected_domain.capitalize()}</strong> | 
                    Language: <strong>{LANGUAGES[selected_lang]['name']}</strong>
                </div>

                {"" if not vapi_key else""}
                <div style="margin-top:1rem">
                    <div id="vapi-sdk-container"></div>
                </div>
                 
                

                <style>
                @keyframes pulse-green {{
                    0%   {{ box-shadow: 0 0 0 0 rgba(52,168,83,0.4); }}
                    70%  {{ box-shadow: 0 0 0 20px rgba(52,168,83,0); }}
                    100% {{ box-shadow: 0 0 0 0 rgba(52,168,83,0); }}
                }}
                </style>
                <script>
                // Timer
                let sec = 0;
                setInterval(() => {{
                    sec++;
                    const m = String(Math.floor(sec/60)).padStart(2,'0');
                    const s = String(sec%60).padStart(2,'0');
                    const el = document.getElementById('timer');
                    if(el) el.textContent = m+':'+s;
                }}, 1000);

                {""if not vapi_key else""}
                // Load Vapi SDK
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/dist/vapi.js';
                script.onload = () => {{
                    const vapi = new Vapi('{vapi_key}');
                    vapi.start('{assistant_id}');
                }};
                document.head.appendChild(script);
                
                </script>
            </div>
            """

            components.html(vapi_widget_html, height=280, scrolling=False)

            col_end, col_save = st.columns(2)
            with col_end:
                if st.button("🔴 End Call", type="secondary", use_container_width=True, key="end_call"):
                    if st.session_state.call_id:
                        vapi_mgr.end_call(st.session_state.call_id)

                    # Save to history
                    call_record = {
                        "id": st.session_state.call_id or f"call_{uuid.uuid4().hex[:8]}",
                        "domain": selected_domain,
                        "language": selected_lang,
                        "timestamp": datetime.now().strftime("%H:%M %d/%m/%Y"),
                        "status": "completed",
                    }
                    st.session_state.call_history.append(call_record)

                    # Save to Qdrant
                    qdrant_mgr.save_interaction(
                        user_id=user_id,
                        interaction={
                            "query": f"Voice call - {selected_domain}",
                            "response": "Voice call completed",
                            "domain": selected_domain,
                            "language": selected_lang,
                            "session_id": st.session_state.voice_session_id,
                            "call_id": call_record["id"],
                        },
                    )

                    st.session_state.call_active = False
                    st.session_state.call_id = None
                    render_success("Call ended & saved to your history")
                    time.sleep(1)
                    st.rerun()

            with col_save:
                if st.button("📋 Get Transcript", use_container_width=True, key="get_transcript"):
                    if st.session_state.call_id:
                        transcript = vapi_mgr.get_transcript(st.session_state.call_id)
                        if transcript:
                            st.session_state.last_transcript = transcript
                    else:
                        st.session_state.last_transcript = (
                            "Sample Transcript:\n\n"
                            "User: I need help with my health.\n"
                            "Vaani: Of course! I can help you with health information. "
                            "Please tell me your symptoms or what kind of health guidance you need.\n"
                            "User: I have a fever since two days.\n"
                            "Vaani: I'm sorry to hear that. For a fever lasting more than 2 days, "
                            "it's important to see a doctor. Stay hydrated, rest well, and take paracetamol "
                            "if the temperature is above 99°F. If fever crosses 103°F, please go to a hospital immediately."
                        )
                    st.rerun()

        # ── Transcript Display ────────────────────────────────
        if "last_transcript" in st.session_state and st.session_state.last_transcript:
            with st.expander("📋 Last Call Transcript", expanded=True):
                st.text_area("Transcript", st.session_state.last_transcript, height=150, key="transcript_text")
                if st.button("Save to History", key="save_transcript"):
                    qdrant_mgr.save_interaction(
                        user_id=user_id,
                        interaction={
                            "query": "Voice transcript",
                            "response": st.session_state.last_transcript[:500],
                            "domain": selected_domain,
                            "language": selected_lang,
                            "session_id": st.session_state.voice_session_id,
                        },
                    )
                    render_success("Transcript saved for personalization!")

    # ── Call History ──────────────────────────────────────────
    if st.session_state.call_history:
        st.markdown("---")
        st.markdown("#### 📜 Session Call History")
        st.markdown("""
        <table class="vaani-table">
            <thead>
                <tr><th>#</th><th>Domain</th><th>Language</th><th>Time</th><th>Status</th></tr>
            </thead>
            <tbody>
        """ + "".join([
            f"<tr><td>{i+1}</td><td>{c['domain'].capitalize()}</td><td>{c['language'].upper()}</td>"
            f"<td>{c['timestamp']}</td><td><span class='badge badge-green'>✓ {c['status']}</span></td></tr>"
            for i, c in enumerate(reversed(st.session_state.call_history[-5:]))
        ]) + "</tbody></table>", unsafe_allow_html=True)

    # ── Tips ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 💡 Tips for Better Interaction")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_info("Speak clearly and slowly — Vaani works better with clear pronunciation")
    with col2:
        render_info("State your question simply — 'I need help with fever' works great")
    with col3:
        render_info("Use your preferred language — Vaani understands regional accents")

    render_footer()
