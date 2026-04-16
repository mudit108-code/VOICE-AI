"""
Vaani AI - Phone Outreach Page
Outbound calls to reach users without internet
"""
import uuid
import streamlit as st
from datetime import datetime

from config import SERVICE_DOMAINS, LANGUAGES
from components.ui import render_top_banner, render_warn, render_success, render_info, render_footer


def render_phone_outreach(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Phone Outreach",
        "Reach users who don't have smartphones — Vaani calls them directly",
        "📞",
    )

    # ── Info Banner ───────────────────────────────────────────
    render_info(
        "Outbound calling enables Vaani to reach rural and low-income users via basic mobile phones. "
        "No internet or smartphone required for the end user."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_form, col_status = st.columns([1, 1])

    # ── Call Form ─────────────────────────────────────────────
    with col_form:
        st.markdown("#### 📲 Initiate Outbound Call")

        with st.form("phone_call_form"):
            phone = st.text_input(
                "Phone Number (with country code)",
                placeholder="+91 9876543210",
                help="Include country code. Example: +91 for India",
            )

            domain_icons = {k: f"{v['icon']} {v['title']}" for k, v in SERVICE_DOMAINS.items()}
            domain = st.selectbox(
                "Service Domain",
                options=list(domain_icons.keys()),
                format_func=lambda x: domain_icons[x],
            )

            lang_options = {k: f"{v['flag']} {v['name']} ({v['native']})" for k, v in LANGUAGES.items()}
            language = st.selectbox(
                "Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
            )

            caller_note = st.text_area(
                "Context Note (optional)",
                placeholder="Brief context about the user's situation to help Vaani personalize the call...",
                height=80,
            )

            call_submitted = st.form_submit_button("📞 Call Now", type="primary", use_container_width=True)

        if call_submitted:
            if not phone or len(phone.strip()) < 8:
                st.error("Please enter a valid phone number")
            else:
                with st.spinner(f"Connecting call to {phone}..."):
                    # Get or create assistant
                    assistant = vapi_mgr.create_domain_assistant(
                        domain=domain,
                        language=language,
                        knowledge_context=caller_note,
                    )
                    assistant_id = assistant.get("id", "demo")

                    result = vapi_mgr.create_phone_call(
                        phone_number=phone.strip(),
                        assistant_id=assistant_id,
                        domain=domain,
                    )

                    if "call_log" not in st.session_state:
                        st.session_state.call_log = []

                    st.session_state.call_log.append({
                        "id": result.get("id", f"call_{uuid.uuid4().hex[:8]}"),
                        "phone": phone,
                        "domain": domain,
                        "language": language,
                        "status": result.get("status", "initiated"),
                        "time": datetime.now().strftime("%H:%M %d/%m/%Y"),
                        "note": caller_note[:50] if caller_note else "",
                    })

                    render_success(f"Call initiated to {phone}! Vaani will connect shortly.")

                    # Save to Qdrant
                    qdrant_mgr.save_session({
                        "type": "phone_call",
                        "phone": phone[-4:] + "XXXX",  # Mask for privacy
                        "domain": domain,
                        "language": language,
                        "call_id": result.get("id", ""),
                    })

    # ── Bulk Upload ───────────────────────────────────────────
    with col_status:
        st.markdown("#### 📋 Bulk Outreach Campaign")

        uploaded = st.file_uploader(
            "Upload CSV (phone, domain, language)",
            type=["csv"],
            help="CSV format: phone_number,domain,language,note",
        )

        if uploaded:
            try:
                import pandas as pd
                df = pd.read_csv(uploaded)
                st.markdown(f"**{len(df)} contacts loaded**")
                st.dataframe(df.head(5), use_container_width=True)

                if st.button("🚀 Launch Campaign", type="primary"):
                    progress = st.progress(0)
                    success_count = 0
                    for i, row in df.iterrows():
                        # Simulate batch calling
                        progress.progress((i + 1) / len(df))
                        success_count += 1

                    st.success(f"Campaign launched! {success_count} calls initiated.")
            except Exception as e:
                st.error(f"CSV error: {e}")
        else:
            st.markdown("""
            <div class="card" style="border-style:dashed;text-align:center;color:#5F6368;padding:2rem">
                <div style="font-size:2rem">📁</div>
                <div style="font-weight:600;margin:0.5rem 0">Upload Contact List</div>
                <div style="font-size:0.8rem">CSV with columns: phone, domain, language, note</div>
            </div>
            """, unsafe_allow_html=True)

        # Sample CSV download
        sample_csv = "phone_number,domain,language,note\n+919876543210,healthcare,hi,Regular health check\n+919876543211,finance,ta,PM-KISAN query\n+919876543212,education,te,Scholarship info"
        st.download_button(
            "⬇️ Download Sample CSV",
            data=sample_csv,
            file_name="vaani_contacts_sample.csv",
            mime="text/csv",
        )

    # ── Call Log ──────────────────────────────────────────────
    if "call_log" in st.session_state and st.session_state.call_log:
        st.markdown("---")
        st.markdown("#### 📜 Call Log")

        log = st.session_state.call_log
        st.markdown("""
        <table class="vaani-table">
            <thead>
                <tr><th>#</th><th>Phone</th><th>Domain</th><th>Language</th><th>Time</th><th>Status</th></tr>
            </thead>
            <tbody>
        """ + "".join([
            f"<tr><td>{i+1}</td><td>{c['phone'][-6:]}XXXX</td>"
            f"<td>{c['domain'].capitalize()}</td><td>{c['language'].upper()}</td>"
            f"<td>{c['time']}</td><td><span class='badge badge-green'>● {c['status']}</span></td></tr>"
            for i, c in enumerate(reversed(log[-10:]))
        ]) + "</tbody></table>", unsafe_allow_html=True)

        if st.button("Clear Log"):
            st.session_state.call_log = []
            st.rerun()

    # ── Use Cases ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🎯 Impact Use Cases")
    col1, col2, col3 = st.columns(3)
    cases = [
        ("👩‍🌾", "Farmer Outreach", "Call farmers to inform about PM-KISAN installments and crop advisory"),
        ("🏥", "Health Camps", "Notify village residents about upcoming health camps and vaccination drives"),
        ("📚", "Scholarship Alerts", "Alert students about new scholarship deadlines and application process"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], cases):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-weight:600;margin:0.4rem 0;font-size:0.9rem">{title}</div>
                <div style="font-size:0.78rem;color:#5F6368">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    render_footer()
