"""
Vaani AI - Chat Interface Page
Text-based interaction with RAG via Qdrant
"""
import uuid
import requests
import streamlit as st
from datetime import datetime

from config import SERVICE_DOMAINS, LANGUAGES, OPENAI_API_KEY
from components.ui import render_top_banner, render_info, render_footer


def get_ai_response(query: str, domain: str, knowledge_ctx: str, user_ctx: str, lang: str) -> str:
    """Get AI response using OpenAI or fallback rule-based."""
    if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            system = f"""You are Vaani, a helpful AI assistant for {domain} services. 
            Respond in {LANGUAGES.get(lang, {}).get('name', 'English')}.
            Use simple, clear language. Be warm and patient.
            
            Knowledge base: {knowledge_ctx[:800]}
            User history: {user_ctx[:400]}
            """
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": query}],
                max_tokens=300,
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception:
            pass

    # Fallback: knowledge-based response
    if knowledge_ctx:
        snippets = knowledge_ctx[:600]
        return (
            f"Based on available information:\n\n{snippets}\n\n"
            f"For more detailed guidance on '{query}', please use the Voice Assistant to speak with Vaani directly. "
            f"You can also call government helplines mentioned above for immediate assistance."
        )
    return (
        f"I understand you're asking about {domain}. While I'm in demo mode, "
        f"I can tell you that for {domain} services, the government provides multiple "
        f"free assistance programs. Please configure your OpenAI API key for full AI responses, "
        f"or use the Voice Assistant powered by Vapi."
    )


def render_chat(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Chat Interface",
        "Text-based interaction with RAG-powered AI — Qdrant retrieves context for every message",
        "💬",
    )

    # ── Init ──────────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_domain" not in st.session_state:
        st.session_state.chat_domain = "healthcare"
    if "chat_lang" not in st.session_state:
        st.session_state.chat_lang = "en"

    # ── Config Row ────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        domain_icons = {k: f"{v['icon']} {v['title']}" for k, v in SERVICE_DOMAINS.items()}
        st.session_state.chat_domain = st.selectbox(
            "Domain",
            options=list(domain_icons.keys()),
            format_func=lambda x: domain_icons[x],
            key="chat_domain_sel",
        )
    with col2:
        lang_options = {k: f"{v['flag']} {v['name']}" for k, v in LANGUAGES.items()}
        st.session_state.chat_lang = st.selectbox(
            "Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            key="chat_lang_sel",
        )
    with col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    with col4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("💾 Save", use_container_width=True):
            if "user_id" in st.session_state and st.session_state.chat_messages:
                for msg in st.session_state.chat_messages:
                    if msg["role"] == "user":
                        qdrant_mgr.save_interaction(
                            user_id=st.session_state.user_id,
                            interaction={
                                "query": msg["content"],
                                "response": "",
                                "domain": st.session_state.chat_domain,
                                "language": st.session_state.chat_lang,
                                "session_id": st.session_state.get("voice_session_id", "chat"),
                            },
                        )
                st.success("Saved to your profile!")

    # ── Chat Display ──────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_messages:
            # Welcome message
            domain = st.session_state.chat_domain
            lang = st.session_state.chat_lang
            lang_name = LANGUAGES.get(lang, {}).get("name", "English")
            welcome = f"Hello! I'm Vaani 🙏 I'm here to help you with {SERVICE_DOMAINS[domain]['title']} services in {lang_name}. What would you like to know?"
            st.session_state.chat_messages.append({"role": "assistant", "content": welcome, "time": datetime.now().strftime("%H:%M")})

        # Render messages
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-msg user">
                    <div class="chat-bubble user">{msg['content']}</div>
                    <div style="font-size:1.2rem">👤</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-msg">
                    <div style="font-size:1.2rem">🤖</div>
                    <div class="chat-bubble ai">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

        # Show RAG sources if available
        if "last_sources" in st.session_state and st.session_state.last_sources:
            with st.expander("📚 Sources retrieved from Qdrant", expanded=False):
                for src in st.session_state.last_sources[:3]:
                    score = int(src.get("score", 0) * 100)
                    st.markdown(f"""
                    <div style="background:#F8F9FA;border-radius:6px;padding:0.5rem 0.7rem;margin-bottom:0.4rem;font-size:0.8rem">
                        <span style="color:#1A73E8;font-weight:600">{score}% relevance</span> · 
                        <span style="color:#5F6368">{src.get('category', 'info')}</span><br>
                        {src['text'][:120]}...
                    </div>
                    """, unsafe_allow_html=True)

    # ── Quick Prompts ─────────────────────────────────────────
    domain = st.session_state.chat_domain
    quick_prompts = {
        "healthcare": ["What are symptoms of diabetes?", "How to get Ayushman card?", "Nearest health center", "Medicine for fever"],
        "finance": ["What is PM-KISAN?", "How to open Jan Dhan account?", "I need a loan", "Report bank fraud"],
        "education": ["Scholarships for my child", "Free coaching programs", "How to apply NSP?", "RTE admission help"],
        "agriculture": ["Crop insurance details", "Weather forecast for farming", "Kisan Call Centre", "Best crops for monsoon"],
        "legal": ["How to file RTI?", "My rights as a worker", "Domestic violence help", "Free legal aid"],
        "employment": ["Find job in my area", "MGNREGA work card", "Free skill training", "Govt job vacancies"],
    }

    st.markdown("**Quick Prompts:**")
    prompts = quick_prompts.get(domain, [])
    cols = st.columns(len(prompts))
    selected_prompt = None
    for col, prompt in zip(cols, prompts):
        with col:
            if st.button(prompt, key=f"qp_{prompt}", use_container_width=True):
                selected_prompt = prompt

    # ── Input ─────────────────────────────────────────────────
    with st.form("chat_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            user_input = st.text_input(
                "Message",
                placeholder=f"Ask Vaani about {SERVICE_DOMAINS[domain]['title']}...",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Send →", type="primary", use_container_width=True)

    # Process selected quick prompt
    if selected_prompt:
        user_input = selected_prompt
        submitted = True

    if submitted and user_input:
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M"),
        })

        # Retrieve from Qdrant
        kb_results = qdrant_mgr.search_knowledge(
            user_input, domain=domain, language=st.session_state.chat_lang, top_k=4
        )
        kb_text = "\n".join([r["text"] for r in kb_results])
        st.session_state.last_sources = kb_results

        # Get user context
        user_id = st.session_state.get("user_id", "anonymous")
        user_ctx_list = qdrant_mgr.get_user_context(user_id, user_input, top_k=2)
        user_ctx = "\n".join([f"Q: {u['query']}" for u in user_ctx_list])

        # Get AI response
        with st.spinner("Vaani is thinking..."):
            response = get_ai_response(
                query=user_input,
                domain=domain,
                knowledge_ctx=kb_text,
                user_ctx=user_ctx,
                lang=st.session_state.chat_lang,
            )

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M"),
        })

        # Save interaction to Qdrant
        qdrant_mgr.save_interaction(
            user_id=user_id,
            interaction={
                "query": user_input,
                "response": response[:500],
                "domain": domain,
                "language": st.session_state.chat_lang,
                "session_id": st.session_state.get("voice_session_id", "chat"),
            },
        )

        st.rerun()

    # ── Info Bar ──────────────────────────────────────────────
    render_info(
        "All responses are retrieved from Qdrant vector database using semantic search "
        "for contextually accurate, personalized answers."
    )
    render_footer()
