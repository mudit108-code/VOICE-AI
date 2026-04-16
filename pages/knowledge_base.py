"""
Vaani AI - Knowledge Base Management Page
Add, search, and manage the Qdrant vector knowledge base
"""
import streamlit as st
from datetime import datetime

from config import SERVICE_DOMAINS, LANGUAGES
from components.ui import render_top_banner, render_success, render_warn, render_info, render_footer
from utils.qdrant_manager import seed_knowledge_base, SEED_KNOWLEDGE


def render_knowledge_base(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Knowledge Base",
        "Manage the Qdrant vector database — Add documents, search semantically, track coverage",
        "🧠",
    )

    qdrant_status = qdrant_mgr.get_status()
    if not qdrant_status["connected"]:
        render_warn("Qdrant running in demo mode. Connect a live Qdrant instance to persist knowledge.")

    tab1, tab2, tab3 = st.tabs(["🔍 Search", "➕ Add Documents", "📊 Database Status"])

    # ── Tab 1: Search ─────────────────────────────────────────
    with tab1:
        st.markdown("#### Semantic Search — Test Knowledge Retrieval")
        render_info("Uses Qdrant vector similarity search to find the most relevant knowledge for any query.")

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search_query = st.text_input("Search Query", placeholder="e.g., How to get PM-KISAN benefit?", label_visibility="collapsed")
        with col2:
            domain_filter = st.selectbox("Domain", ["all"] + list(SERVICE_DOMAINS.keys()),
                                          format_func=lambda x: "All Domains" if x == "all" else SERVICE_DOMAINS[x]["icon"] + " " + SERVICE_DOMAINS[x]["title"],
                                          label_visibility="collapsed")
        with col3:
            top_k = st.selectbox("Results", [3, 5, 10], label_visibility="collapsed")

        if st.button("🔍 Search", type="primary") and search_query:
            with st.spinner("Searching Qdrant..."):
                results = qdrant_mgr.search_knowledge(
                    search_query,
                    domain=domain_filter if domain_filter != "all" else None,
                    top_k=top_k,
                )

            if results:
                st.markdown(f"**{len(results)} results found**")
                for i, r in enumerate(results):
                    score_pct = int(r.get("score", 0) * 100)
                    score_color = "#2E7D32" if score_pct >= 80 else "#E65100" if score_pct >= 60 else "#5F6368"
                    domain_info = SERVICE_DOMAINS.get(r.get("domain", ""), {})
                    icon = domain_info.get("icon", "📄")

                    st.markdown(f"""
                    <div class="card">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                            <div style="display:flex;align-items:center;gap:0.5rem">
                                <span>{icon}</span>
                                <span style="font-weight:600;font-size:0.88rem">{r.get('domain', 'general').capitalize()}</span>
                                <span class="badge badge-blue">{r.get('category', 'info')}</span>
                            </div>
                            <div style="font-weight:700;color:{score_color};font-size:0.85rem">{score_pct}% match</div>
                        </div>
                        <div style="font-size:0.88rem;line-height:1.5;color:#202124">{r['text']}</div>
                        <div style="margin-top:0.4rem;font-size:0.75rem;color:#5F6368">Source: {r.get('source', 'manual')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No results found. Try a different query or add more documents.")

    # ── Tab 2: Add Documents ──────────────────────────────────
    with tab2:
        col_manual, col_bulk = st.columns([1, 1])

        with col_manual:
            st.markdown("#### ✍️ Add Single Document")
            with st.form("add_doc_form"):
                doc_text = st.text_area("Document Content", placeholder="Enter the knowledge content here...", height=120)
                col_a, col_b = st.columns(2)
                with col_a:
                    doc_domain = st.selectbox("Domain", list(SERVICE_DOMAINS.keys()),
                                               format_func=lambda x: SERVICE_DOMAINS[x]["icon"] + " " + SERVICE_DOMAINS[x]["title"])
                    doc_lang = st.selectbox("Language", list(LANGUAGES.keys()),
                                             format_func=lambda x: LANGUAGES[x]["flag"] + " " + LANGUAGES[x]["name"])
                with col_b:
                    doc_category = st.text_input("Category", placeholder="e.g., schemes, emergency, rights")
                    doc_source = st.text_input("Source", placeholder="e.g., govt, WHO, NGO")

                add_submitted = st.form_submit_button("➕ Add Document", type="primary", use_container_width=True)

            if add_submitted and doc_text:
                with st.spinner("Indexing in Qdrant..."):
                    result = qdrant_mgr.upsert_knowledge([{
                        "text": doc_text,
                        "domain": doc_domain,
                        "language": doc_lang,
                        "category": doc_category or "info",
                        "source": doc_source or "manual",
                        "metadata": {"added_at": datetime.utcnow().isoformat()},
                    }])
                render_success(f"Document indexed successfully! Status: {result['status']}")

        with col_bulk:
            st.markdown("#### 📦 Bulk Operations")

            col_seed, col_up = st.columns(2)
            with col_seed:
                if st.button("🌱 Seed Default KB", use_container_width=True, help="Load pre-built government schemes & health data"):
                    with st.spinner(f"Seeding {len(SEED_KNOWLEDGE)} documents..."):
                        result = seed_knowledge_base(qdrant_mgr)
                    render_success(f"Seeded {result['count']} documents into Qdrant!")
                    st.session_state.seed_done = True

            with col_up:
                st.markdown("Upload JSON KB:")
                kb_file = st.file_uploader("Upload JSON", type=["json"], label_visibility="collapsed")
                if kb_file:
                    import json
                    docs = json.load(kb_file)
                    if st.button("📤 Index File", use_container_width=True):
                        with st.spinner("Indexing..."):
                            result = qdrant_mgr.upsert_knowledge(docs)
                        render_success(f"Indexed {result['count']} documents!")

            # Seed preview
            st.markdown("#### 📋 Default Knowledge Preview")
            for doc in SEED_KNOWLEDGE[:6]:
                domain_info = SERVICE_DOMAINS.get(doc["domain"], {})
                st.markdown(f"""
                <div style="background:#F8F9FA;border-radius:6px;padding:0.5rem 0.7rem;margin-bottom:0.3rem;font-size:0.78rem">
                    <span>{domain_info.get('icon','📄')}</span>
                    <span style="font-weight:600;color:#1A73E8"> {doc['domain'].capitalize()}</span>
                    <span style="color:#5F6368"> · {doc['category']}</span><br>
                    {doc['text'][:100]}...
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"<div style='color:#5F6368;font-size:0.78rem'>+{len(SEED_KNOWLEDGE)-6} more documents available</div>", unsafe_allow_html=True)

    # ── Tab 3: DB Status ──────────────────────────────────────
    with tab3:
        st.markdown("#### 📊 Qdrant Database Status")

        global_stats = qdrant_mgr.get_global_stats()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card"><div class="metric-val">{global_stats.get('knowledge_docs', 0)}</div><div class="metric-label">Knowledge Docs</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><div class="metric-val">{global_stats.get('total_queries', 0)}</div><div class="metric-label">Total Queries</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><div class="metric-val">384</div><div class="metric-label">Vector Dimensions</div></div>""", unsafe_allow_html=True)
        with col4:
            mode = qdrant_status.get("mode", "demo")
            color = "#2E7D32" if mode == "live" else "#E65100"
            st.markdown(f"""<div class="metric-card"><div class="metric-val" style="color:{color};font-size:1.2rem">{mode.upper()}</div><div class="metric-label">Connection Mode</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Collections info
        st.markdown("#### Collections")
        collections = [
            {"name": "vaani_knowledge_base", "desc": "Domain knowledge & govt schemes", "docs": global_stats.get('knowledge_docs', 0), "type": "Knowledge"},
            {"name": "vaani_user_history", "desc": "User interaction history for personalization", "docs": global_stats.get('total_queries', 0), "type": "History"},
            {"name": "vaani_sessions", "desc": "Session metadata for analytics", "docs": 0, "type": "Sessions"},
        ]
        st.markdown("""
        <table class="vaani-table">
            <thead><tr><th>Collection</th><th>Type</th><th>Description</th><th>Documents</th><th>Status</th></tr></thead>
            <tbody>
        """ + "".join([
            f"<tr><td><code>{c['name']}</code></td><td><span class='badge badge-blue'>{c['type']}</span></td>"
            f"<td style='font-size:0.8rem;color:#5F6368'>{c['desc']}</td><td>{c['docs']}</td>"
            f"<td><span class='badge badge-green'>✓ Active</span></td></tr>"
            for c in collections
        ]) + "</tbody></table>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <strong>Qdrant URL:</strong> {qdrant_status.get('url', 'localhost:6333')}<br>
            <strong>Embedding Model:</strong> all-MiniLM-L6-v2 (384 dimensions, cosine similarity)<br>
            <strong>Mode:</strong> {qdrant_status.get('mode', 'demo').upper()} — {"Data persisted to Qdrant cluster" if qdrant_status.get('connected') else "Running with mock data — configure Qdrant URL in Settings"}
        </div>
        """, unsafe_allow_html=True)

    render_footer()
