"""
Vaani AI - Analytics Dashboard
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from components.ui import render_top_banner, render_footer
from config import SERVICE_DOMAINS, LANGUAGES


# ── Demo Data ────────────────────────────────────────────────
def get_demo_analytics():
    return {
        "daily_calls": {
            "dates": ["Jan 10", "Jan 11", "Jan 12", "Jan 13", "Jan 14", "Jan 15", "Jan 16"],
            "calls": [42, 58, 73, 65, 89, 94, 112],
            "users": [38, 51, 67, 60, 82, 88, 103],
        },
        "domain_distribution": {
            "Healthcare": 38,
            "Finance": 22,
            "Education": 18,
            "Agriculture": 12,
            "Legal": 6,
            "Employment": 4,
        },
        "language_distribution": {
            "Hindi": 35,
            "English": 20,
            "Tamil": 15,
            "Telugu": 12,
            "Bengali": 8,
            "Others": 10,
        },
        "satisfaction": {
            "labels": ["Very Helpful", "Helpful", "Neutral", "Not Helpful"],
            "values": [52, 31, 12, 5],
        },
        "hourly": {
            "hours": list(range(0, 24)),
            "calls": [2, 1, 0, 0, 1, 3, 8, 15, 22, 28, 31, 25, 20, 24, 26, 28, 30, 27, 22, 18, 14, 10, 7, 4],
        },
        "state_data": {
            "UP": 280, "MH": 210, "TN": 185, "WB": 165, "RJ": 142,
            "AP": 138, "KA": 125, "GJ": 118, "MP": 95, "KL": 87,
        },
    }


def render_analytics(vapi_mgr, qdrant_mgr):
    render_top_banner(
        "Analytics Dashboard",
        "Real-time impact tracking — Usage, reach, and accessibility metrics",
        "📊",
    )

    data = get_demo_analytics()
    global_stats = qdrant_mgr.get_global_stats()

    # ── KPI Row ───────────────────────────────────────────────
    kpis = [
        ("1,428", "Total Queries", "#1A73E8"),
        ("312", "Unique Users", "#34A853"),
        ("6", "Domains Active", "#FBBC04"),
        ("15+", "Languages", "#EA4335"),
        ("4.2★", "Avg Rating", "#9C27B0"),
        ("2:34", "Avg Call Duration", "#00BCD4"),
    ]
    cols = st.columns(6)
    for col, (val, label, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📈 Daily Usage Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["daily_calls"]["dates"],
            y=data["daily_calls"]["calls"],
            name="Voice Calls",
            line=dict(color="#1A73E8", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(26,115,232,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=data["daily_calls"]["dates"],
            y=data["daily_calls"]["users"],
            name="Unique Users",
            line=dict(color="#34A853", width=2, dash="dot"),
        ))
        fig.update_layout(
            height=260, margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            font=dict(family="DM Sans"),
            xaxis=dict(showgrid=False, showline=True, linecolor="#DADCE0"),
            yaxis=dict(showgrid=True, gridcolor="#F1F3F4", showline=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🌐 Domain Distribution")
        fig2 = go.Figure(go.Pie(
            labels=list(data["domain_distribution"].keys()),
            values=list(data["domain_distribution"].values()),
            hole=0.55,
            marker_colors=["#1A73E8", "#34A853", "#FBBC04", "#EA4335", "#9C27B0", "#00BCD4"],
        ))
        fig2.update_traces(textposition="inside", textinfo="percent", textfont_size=10)
        fig2.update_layout(
            height=260, margin=dict(l=0, r=0, t=20, b=0),
            showlegend=True,
            legend=dict(font=dict(size=9), orientation="v"),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Charts Row 2 ──────────────────────────────────────────
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown("#### 🗣️ Language Breakdown")
        langs = data["language_distribution"]
        fig3 = go.Figure(go.Bar(
            x=list(langs.values()),
            y=list(langs.keys()),
            orientation="h",
            marker_color=["#1A73E8", "#34A853", "#FBBC04", "#EA4335", "#9C27B0", "#00BCD4"],
        ))
        fig3.update_layout(
            height=230, margin=dict(l=10, r=20, t=10, b=10),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="DM Sans", size=11),
            xaxis=dict(showgrid=True, gridcolor="#F1F3F4"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### ⏰ Hourly Activity")
        hours = data["hourly"]
        fig4 = go.Figure(go.Bar(
            x=hours["hours"],
            y=hours["calls"],
            marker_color=["#1A73E8" if c == max(hours["calls"]) else "#DADCE0" for c in hours["calls"]],
        ))
        fig4.update_layout(
            height=230, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="DM Sans", size=10),
            xaxis=dict(title="Hour of Day", showgrid=False, dtick=6),
            yaxis=dict(showgrid=True, gridcolor="#F1F3F4"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col5:
        st.markdown("#### 😊 User Satisfaction")
        sat = data["satisfaction"]
        fig5 = go.Figure(go.Pie(
            labels=sat["labels"],
            values=sat["values"],
            hole=0.6,
            marker_colors=["#34A853", "#FBBC04", "#FF9800", "#EA4335"],
        ))
        fig5.update_layout(
            height=230, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(font=dict(size=9)),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig5, use_container_width=True)

    # ── State Heatmap ─────────────────────────────────────────
    st.markdown("#### 🗺️ Geographic Reach (Top States)")
    states = data["state_data"]
    fig6 = go.Figure(go.Bar(
        x=list(states.keys()),
        y=list(states.values()),
        marker=dict(
            color=list(states.values()),
            colorscale=[[0, "#E8F0FE"], [1, "#1A73E8"]],
            showscale=False,
        ),
        text=list(states.values()),
        textposition="outside",
    ))
    fig6.update_layout(
        height=240, margin=dict(l=20, r=20, t=10, b=20),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans", size=11),
        xaxis=dict(showgrid=False, showline=True, linecolor="#DADCE0"),
        yaxis=dict(showgrid=True, gridcolor="#F1F3F4", title="Users"),
    )
    st.plotly_chart(fig6, use_container_width=True)

    # ── Impact Summary ────────────────────────────────────────
    st.markdown("#### 🌟 Social Impact Metrics")
    impact_cols = st.columns(4)
    impacts = [
        ("🏘️", "~280", "Rural Users Served", "Users from villages & remote areas"),
        ("📵", "~94", "Feature Phone Users", "Reached via outbound calls"),
        ("👩", "58%", "Women Users", "Gender inclusion in digital services"),
        ("⚡", "2.3s", "Avg Response Time", "From query to voice answer"),
    ]
    for col, (icon, val, label, desc) in zip(impact_cols, impacts):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center">
                <div style="font-size:1.8rem">{icon}</div>
                <div style="font-family:'Plus Jakarta Sans';font-weight:700;font-size:1.5rem;color:#1A73E8">{val}</div>
                <div style="font-weight:600;font-size:0.82rem;margin-top:2px">{label}</div>
                <div style="font-size:0.75rem;color:#5F6368;margin-top:2px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── User Profile ──────────────────────────────────────────
    if "user_id" in st.session_state:
        st.markdown("---")
        st.markdown("#### 👤 Your Usage Profile")
        user_stats = qdrant_mgr.get_user_stats(st.session_state.user_id)
        ucols = st.columns(4)
        stats_items = [
            (user_stats.get("total_interactions", 0), "Your Interactions"),
            (len(user_stats.get("domains_used", [])), "Domains Used"),
            (len(user_stats.get("languages_used", [])), "Languages Used"),
            (user_stats.get("last_active", "—")[:10] or "—", "Last Active"),
        ]
        for col, (val, label) in zip(ucols, stats_items):
            with col:
                st.markdown(f"""<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

    render_footer()
