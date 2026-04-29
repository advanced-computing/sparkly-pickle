import streamlit as st

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding:2rem 0 1.5rem 0;">
        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.15em;
                    color:#4A7FB5;font-weight:700;margin-bottom:0.8rem;">
            NYC Open Data · 2026 Live · Updated Hourly
        </div>
        <h1 style="font-family:'JetBrains Mono',monospace;font-size:2.6rem;font-weight:600;
                   color:#0F172A;line-height:1.15;margin:0 0 1rem 0;letter-spacing:-0.02em;">
            NYC Traffic Safety<br>Intelligence Dashboard
        </h1>
        <p style="color:#475569;font-size:1.05rem;max-width:680px;margin:0;line-height:1.75;">
            A diagnostic tool for understanding where NYC's traffic safety problem actually lives —
            and why a one-size-fits-all citywide policy is the wrong answer.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Stat cards ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, num, label, sub in [
    (c1, "2026", "Data Year", "Live-refreshed every hour"),
    (c2, "2", "Datasets Merged", "Person + Crash records"),
    (c3, "5", "NYC Boroughs", "Citywide breakdown"),
    (c4, "4", "Analysis Modules", "Big picture → policy"),
]:
    with col:
        st.markdown(
            f"""
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                        padding:1.4rem 1.2rem;text-align:center;
                        box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;
                            color:#6F9FCF;line-height:1;margin-bottom:0.4rem;font-weight:700;">{num}</div>
                <div style="font-weight:700;color:#0F172A;font-size:0.78rem;
                            text-transform:uppercase;letter-spacing:0.1em;
                            margin-bottom:0.3rem;">{label}</div>
                <div style="color:#64748B;font-size:0.78rem;line-height:1.5;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Central argument ────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;"
    "color:#0F172A;margin-bottom:0.8rem;font-size:1.2rem;'>The Central Argument</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
        <div style='color:#334155;font-size:0.95rem;line-height:1.8;'>
            NYC's traffic safety problem is not uniform. Crash <strong>causes</strong>,
            <strong>severity</strong>, and <strong>victim profiles</strong> look very different
            depending on which borough you're in and what time of day it is. A policy that treats
            all boroughs and all hours the same will systematically under-serve the places and
            moments where the risk is actually highest.<br><br>
            This dashboard walks you through the evidence in four steps —
            from the citywide picture, to who bears the risk, to where and when that risk
            concentrates, and finally to the specific policy levers the data supports.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Module cards ─────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;"
    "color:#0F172A;margin-bottom:0.8rem;font-size:1.2rem;'>How To Read This Dashboard</h3>",
    unsafe_allow_html=True,
)

modules = [
    (
        "1.",
        "📊",
        "The Big Picture",
        "Establish the baseline: total crashes, fatalities, and the citywide patterns "
        "that look uniform on the surface.",
    ),
    (
        "2.",
        "👥",
        "Who Bears the Risk",
        "Drill into who is actually getting hurt. Pedestrians and cyclists are a small "
        "share of crash involvements but a large share of deaths.",
    ),
    (
        "3.",
        "🗺️",
        "Where & When",
        "Show how crash causes vary across boroughs and time of day. The citywide "
        "averages hide the real problems.",
    ),
    (
        "4.",
        "🎯",
        "Policy Levers",
        "Synthesize the findings into specific, evidence-backed recommendations for "
        "borough-level and time-specific interventions.",
    ),
]

cols = st.columns(4)
for col, (num, icon, title, desc) in zip(cols, modules):
    with col:
        st.markdown(
            f"""
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                        padding:1.3rem 1.2rem;height:100%;
                        box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.7rem;">
                    <div style="font-family:JetBrains Mono,monospace;font-size:0.9rem;
                                color:#6F9FCF;font-weight:700;">{num}</div>
                    <div style="font-size:1.4rem;">{icon}</div>
                </div>
                <div style="font-weight:700;color:#0F172A;font-size:0.95rem;
                            margin-bottom:0.45rem;font-family:JetBrains Mono,monospace;">{title}</div>
                <div style="color:#64748B;font-size:0.83rem;line-height:1.6;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters note ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="card">
        <div style="display:flex;gap:1rem;align-items:flex-start;">
            <div style="font-size:1.4rem;">🎛️</div>
            <div>
                <div style="font-weight:700;color:#0F172A;margin-bottom:0.3rem;
                            font-family:JetBrains Mono,monospace;font-size:0.95rem;">
                    Use the sidebar filters
                </div>
                <div style="color:#64748B;font-size:0.88rem;line-height:1.65;">
                    Every analytical page (modules 1–4) responds to the borough, person-type,
                    time-period, and date filters in the sidebar. Adjust them to compare
                    boroughs side-by-side, isolate late-night patterns, or zoom in on a
                    specific date window.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Data pipeline note ────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="card">
        <div style="display:flex;gap:1rem;align-items:flex-start;">
            <div style="font-size:1.4rem;">🔄</div>
            <div>
                <div style="font-weight:700;color:#0F172A;margin-bottom:0.3rem;
                            font-family:JetBrains Mono,monospace;font-size:0.95rem;">
                    Live Data Pipeline
                </div>
                <div style="color:#64748B;font-size:0.88rem;line-height:1.65;">
                    Data is pulled directly from the NYC Open Data API, stored in Google BigQuery,
                    and cached for one hour. Each page queries BigQuery in real time —
                    no static snapshots.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Source: NYC Open Data — Motor Vehicle Collisions (Person & Crash) · "
    "Group sparkly-pickle · Yiran Ge · Yizi Qu"
)
