import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="NYC Traffic Safety Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global light theme + SIPA blue ───────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Force fonts ── */
    html, body, .stApp, .stApp * {
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Base — light theme ── */
    .stApp {
        background-color: #F5F7FA;
        color: #1c2536;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] * {
        color: #1c2536 !important;
    }

    /* ── Default text ── */
    .stApp p, .stApp div, .stApp span, .stApp li {
        color: #334155;
    }

    /* ── Headings — JetBrains Mono for a dashboard feel ── */
    h1, h2, h3, h4 {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        color: #1c2536 !important;
        letter-spacing: -0.01em;
    }
    h1 { color: #0F172A !important; }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    [data-testid="stMetricValue"] {
        color: #6F9FCF !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
    }

    /* ── Divider ── */
    hr { border-color: #E2E8F0 !important; }

    /* ── Caption ── */
    .stCaption, small { color: #94A3B8 !important; }

    /* ── Card — generic ── */
    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.3rem 1.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.85rem;
    }

    /* ── Insight box ── */
    .insight-box {
        background: #F0F6FB;
        border-left: 4px solid #6F9FCF;
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.2rem;
        color: #334155;
        font-size: 0.91rem;
        line-height: 1.7;
        margin-top: 0.5rem;
    }

    /* ── Takeaway box ── */
    .takeaway-box {
        background: #F0F6FB;
        border: 1px solid #C9DDEF;
        border-left: 4px solid #6F9FCF;
        border-radius: 0 8px 8px 0;
        padding: 1.1rem 1.3rem;
        color: #334155;
        font-size: 0.92rem;
        line-height: 1.75;
        margin-top: 0.5rem;
    }

    /* ── Formula box ── */
    .formula-box {
        background: #FAFCFE;
        border: 1px dashed #C9DDEF;
        border-radius: 8px;
        padding: 0.85rem 1.2rem;
        margin: 0.6rem 0;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.92rem;
        color: #1c2536;
        line-height: 1.7;
    }
    .formula-box .formula-label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem;
        color: #6F9FCF;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        display: block;
        margin-bottom: 0.4rem;
    }

    /* ── Page label pill ── */
    .page-label {
        display: inline-block;
        background: #E8F0F8;
        color: #4A7FB5;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 0.3rem 0.85rem;
        border-radius: 99px;
        margin-bottom: 0.7rem;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Status pills ── */
    .status-critical {
        display: inline-block;
        background: #FEF2F2;
        color: #B91C1C;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.25rem 0.7rem;
        border-radius: 99px;
        border: 1px solid #FCA5A5;
    }
    .status-warning {
        display: inline-block;
        background: #FFF7ED;
        color: #C2410C;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.25rem 0.7rem;
        border-radius: 99px;
        border: 1px solid #FDBA74;
    }
    .status-normal {
        display: inline-block;
        background: #F0FDF4;
        color: #15803D;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.25rem 0.7rem;
        border-radius: 99px;
        border: 1px solid #86EFAC;
    }

    /* ── Sidebar project card ── */
    .project-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.95rem 1rem;
        margin: 0.5rem 0 1rem 0;
    }
    .project-card .project-eyebrow {
        font-size: 0.62rem;
        font-weight: 700;
        color: #4A7FB5;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
        font-family: 'Inter', sans-serif !important;
    }
    .project-card .project-title {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.3rem;
    }
    .project-card .project-desc {
        font-size: 0.82rem;
        color: #64748B;
        line-height: 1.55;
    }

    /* ── Sidebar section labels ── */
    .sidebar-section-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #94A3B8;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 1rem 0 0.5rem 0;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #FFFFFF;
        color: #1c2536;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: #F0F6FB;
        border-color: #6F9FCF;
        color: #4A7FB5;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: #6F9FCF;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stDownloadButton > button:hover {
        background: #4A7FB5;
        color: #FFFFFF;
    }

    /* ── Selectbox / multiselect ── */
    [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border-color: #E2E8F0 !important;
    }

    /* ── Slider ── */
    [data-testid="stSlider"] > div > div > div > div {
        background: #6F9FCF !important;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }

    /* ── Material Symbols icon fix (fixes _arrow_drop_right showing as text) ── */
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Symbols+Rounded|Material+Symbols+Outlined');

    [data-testid="stExpander"] svg,
    [data-testid="stIconMaterial"],
    span.material-icons,
    span.material-symbols-rounded,
    span.material-symbols-outlined {
        font-family: 'Material Symbols Rounded', 'Material Icons', 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.2rem;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: 'liga';
        font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
    }

    /* ── Body text ── */
    .stMarkdown p { color: #475569 !important; line-height: 1.7; }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #6F9FCF !important; }

    /* ── Investigation context bar ── */
    .context-bar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.7rem 1.1rem;
        margin-bottom: 1rem;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem;
        color: #334155;
    }
    .context-bar .context-label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.62rem;
        font-weight: 700;
        color: #6F9FCF;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-right: 0.5rem;
    }
    .context-bar strong {
        color: #0F172A;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar — logo + project card ────────────────────────────────────────────
with st.sidebar:
    logo_path = Path(__file__).parent / "sipa_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown(
            "<div style='font-family:Lora,serif;font-size:1.1rem;color:#4A7FB5;font-weight:600;'>"
            "Columbia | SIPA</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="project-card">
            <div class="project-eyebrow">NYC Traffic Safety</div>
            <div class="project-title">Precision Policy Lab</div>
            <div class="project-desc">
                Diagnose where, when, and why NYC crashes happen — and where city-wide
                policy is missing the mark.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section-label">Module</div>',
        unsafe_allow_html=True,
    )

# ── Pages ─────────────────────────────────────────────────────────────────────
home_page    = st.Page("main_page.py",     title="Home",                icon="🏙️")
proposal     = st.Page("proposal_page.py", title="Research Proposal",   icon="📋")
overview     = st.Page("page_overview.py", title="1. The Big Picture",  icon="📊")
who          = st.Page("page_who.py",      title="2. Who Bears Risk",   icon="👥")
where_when   = st.Page("page_where.py",    title="3. Where & When",     icon="🗺️")
policy       = st.Page("page_policy.py",   title="4. Policy Levers",    icon="🎯")

pg = st.navigation([home_page, proposal, overview, who, where_when, policy])
pg.run()