"""
Vaani AI - Home Page
"""
import streamlit as st
from components.ui import render_top_banner, render_metric, render_footer


def render_home(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Vaani AI — Voice for Everyone",
        "Breaking digital barriers through intelligent voice AI in 15+ languages",
        "🎙️",
    )

    # ── Status Row ────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        vs = vapi_mgr.get_status()
        color = "#E8F5E9" if vs["connected"] else "#FFF8E1"
        icon = "🟢" if vs["connected"] else "🟡"
        mode = "Live" if vs["connected"] else "Demo"
        st.markdown(f"""
        <div style="background:{color};border-radius:10px;padding:0.75rem 1rem;display:flex;align-items:center;gap:0.5rem">
            <span style="font-size:1.1rem">{icon}</span>
            <div>
                <div style="font-weight:600;font-size:0.85rem">Vapi Voice Engine</div>
                <div style="font-size:0.75rem;color:#5F6368">{mode} Mode</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        qs = qdrant_mgr.get_status()
        color = "#E8F5E9" if qs["connected"] else "#FFF8E1"
        icon = "🟢" if qs["connected"] else "🟡"
        mode = "Live" if qs["connected"] else "Demo"
        st.markdown(f"""
        <div style="background:{color};border-radius:10px;padding:0.75rem 1rem;display:flex;align-items:center;gap:0.5rem">
            <span style="font-size:1.1rem">{icon}</span>
            <div>
                <div style="font-weight:600;font-size:0.85rem">Qdrant Vector DB</div>
                <div style="font-size:0.75rem;color:#5F6368">{mode} Mode</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Global Stats ──────────────────────────────────────────
    stats = qdrant_mgr.get_global_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric(stats.get("total_queries", "1,428"), "Total Voice Queries", "12%")
    with c2: render_metric(stats.get("total_users", "312"), "Active Users", "8%")
    with c3: render_metric(stats.get("knowledge_docs", "847"), "Knowledge Articles")
    with c4: render_metric("15+", "Languages Supported")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────────
    st.markdown("### 🔄 How Vaani AI Works")
    col1, col2, col3, col4 = st.columns(4)
    steps = [
        ("1️⃣", "Speak or Type", "User interacts via voice or text in their language"),
        ("2️⃣", "Vapi Processes", "Voice converted to text, intent understood by AI"),
        ("3️⃣", "Qdrant Retrieves", "Relevant knowledge fetched via semantic search"),
        ("4️⃣", "Voice Response", "Clear, simple answer spoken back in user's language"),
    ]
    for col, (num, title, desc) in zip([col1, col2, col3, col4], steps):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:1rem">
                <div style="font-size:1.8rem">{num}</div>
                <div style="font-weight:600;font-size:0.88rem;margin:0.3rem 0">{title}</div>
                <div style="font-size:0.77rem;color:#5F6368">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Service Domains ───────────────────────────────────────
    st.markdown("### 🌐 Service Domains")
    from config import SERVICE_DOMAINS
    cols = st.columns(3)
    for i, (key, domain) in enumerate(SERVICE_DOMAINS.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="domain-card">
                <div class="icon">{domain['icon']}</div>
                <div class="title">{domain['title']}</div>
                <div class="desc">{domain['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Features ──────────────────────────────────────────────
    st.markdown("### ✨ Key Features")
    col1, col2 = st.columns(2)
    features_left = [
        ("🎙️", "Real Voice Calls", "Powered by Vapi with natural AI voice"),
        ("🔍", "Semantic Search", "Qdrant vector DB for intelligent retrieval"),
        ("🌍", "15+ Languages", "Hindi, Tamil, Telugu, Bengali & more"),
        ("📱", "Mobile-First", "Works on any smartphone, even 2G"),
        ("🏥", "6 Domains", "Health, Finance, Education, Legal, Agri, Jobs"),
        ("🔐", "Privacy First", "No personal data stored without consent"),
    ]
    features_right = [
        ("🧠", "Contextual Memory", "Personalizes over time using Qdrant"),
        ("📞", "Outbound Calls", "Reach users who can't access internet"),
        ("📊", "Usage Analytics", "Track impact and adoption metrics"),
        ("🤝", "Low Literacy", "Simple language for all literacy levels"),
        ("⚡", "RAG Architecture", "Retrieved augmented generation for accuracy"),
        ("🌐", "Offline-Friendly", "Core features work on basic phones"),
    ]
    with col1:
        for icon, title, desc in features_left:
            st.markdown(f"""
            <div style="display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:0.75rem">
                <div style="font-size:1.3rem;margin-top:2px">{icon}</div>
                <div>
                    <div style="font-weight:600;font-size:0.88rem">{title}</div>
                    <div style="font-size:0.78rem;color:#5F6368">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        for icon, title, desc in features_right:
            st.markdown(f"""
            <div style="display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:0.75rem">
                <div style="font-size:1.3rem;margin-top:2px">{icon}</div>
                <div>
                    <div style="font-weight:600;font-size:0.88rem">{title}</div>
                    <div style="font-size:0.78rem;color:#5F6368">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Quick Start ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        🚀 <strong>Quick Start:</strong> Navigate to <strong>Voice Assistant</strong> to start a voice call, 
        or <strong>Chat Interface</strong> for text-based interaction. 
        Go to <strong>Settings</strong> to configure your Vapi & Qdrant API keys.
    </div>
    """, unsafe_allow_html=True)

    render_footer()
