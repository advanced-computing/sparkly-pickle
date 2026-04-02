import streamlit as st

st.set_page_config(
    page_title="NYC Open Data App",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Force font on everything ── */
    html, body, .stApp, .stApp * {
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Base ── */
    .stApp {
        background-color: #0f1117;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0f1117;
        border-right: 1px solid #2a2a3a;
    }
    [data-testid="stSidebar"] * {
        color: #c9c4bc !important;
    }

    /* ── All text defaults ── */
    .stApp p, .stApp div, .stApp span, .stApp li {
        color: #c9c4bc;
    }

    /* ── Headings — Lora serif ── */
    h1, h2, h3, h4 {
        font-family: 'Lora', serif !important;
        font-weight: 500 !important;
        color: #b45309 !important;
        letter-spacing: -0.01em;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #1a1c27;
        border: 1px solid #2a2a3a;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    [data-testid="stMetricValue"] {
        color: #e8e0d4 !important;
        font-size: 1.9rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #7a7060 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Divider ── */
    hr { border-color: #2a2a3a !important; }

    /* ── Caption ── */
    .stCaption, small { color: #4a4640 !important; }

    /* ── Insight box ── */
    .insight-box {
        background: #1a1c27;
        border-left: 3px solid #b45309;
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        color: #b8b0a4;
        font-size: 0.91rem;
        line-height: 1.7;
        margin-top: 0.5rem;
    }

    /* ── Page label pill ── */
    .page-label {
        display: inline-block;
        background: #2a1a0e;
        color: #b45309;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 0.2rem 0.7rem;
        border-radius: 99px;
        margin-bottom: 0.6rem;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #1a1c27 !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 8px !important;
    }

    /* ── Body text ── */
    .stMarkdown p { color: #9b9488 !important; }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #b45309 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

main_page = st.Page("main_page.py", title="Main Page", icon="🎈")
proposal = st.Page("proposal_page.py", title="Research Proposal", icon="📋")
page_2 = st.Page("page_2.py", title="Page 2", icon="❄️")
page_3 = st.Page("page_3.py", title="Page 3", icon="🎉")

pg = st.navigation([main_page, proposal, page_2, page_3])
pg.run()
