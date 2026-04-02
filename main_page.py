import streamlit as st

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding:3rem 0 2rem 0;">
        <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.15em;
                    color:#b45309;font-weight:600;margin-bottom:1rem;">
            NYC Open Data · 2026 Live
        </div>
        <h1 style="font-family:'Lora',serif;font-size:3.2rem;font-weight:400;
                   color:#b45309;line-height:1.15;margin:0 0 1.2rem 0;">
            Motor Vehicle<br>Collisions in New York City
        </h1>
        <p style="color:#9b9488;font-size:1.1rem;max-width:560px;margin:0;line-height:1.8;">
            An interactive look at when, where, and how crashes happen across the five boroughs —
            powered by live BigQuery data updated hourly.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Stat cards — white on dark ────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
for col, num, label, sub in [
    (c1, "2026", "Data Year",        "Live-refreshed every hour from NYC Open Data"),
    (c2, "2",    "Datasets Merged",  "Person-level and crash-level records combined"),
    (c3, "5",    "NYC Boroughs",     "Geographic breakdown across all five boroughs"),
]:
    with col:
        st.markdown(
            f"""
            <div style="background:#ffffff;border-radius:14px;
                        padding:1.6rem 1.4rem;text-align:center;
                        box-shadow:0 2px 12px rgba(0,0,0,0.25);">
                <div style="font-family:'Lora',serif;font-size:2.8rem;
                            color:#b45309;line-height:1;margin-bottom:0.4rem;">{num}</div>
                <div style="font-weight:700;color:#b45309;font-size:0.95rem;
                            margin-bottom:0.4rem;">{label}</div>
                <div style="color:#9b9488;font-size:0.8rem;line-height:1.5;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── What this app explores ────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;"
    "color:#b45309;margin-bottom:1rem;'>What This App Explores</h3>",
    unsafe_allow_html=True,
)

topics = [
    ("👤", "Who gets hurt",
     "Injury and fatality outcomes across pedestrians, cyclists, drivers, and occupants."),
    ("🕐", "When crashes happen",
     "Hour-by-day heatmaps revealing commuter peaks, late-night risk, and weekly rhythms."),
    ("🗺️", "Where risk concentrates",
     "Borough-level crash counts exposing geographic inequality in traffic safety."),
    ("⚠️", "Why crashes occur",
     "Top contributing factors recorded by officers at the scene."),
    ("📉", "Long-term fatality trends",
     "Monthly tracking of pedestrian, cyclist, and motorist fatalities for Vision Zero."),
    ("🛡️", "Safety equipment impact",
     "How seatbelts and airbags affect injury outcomes for drivers and occupants."),
]

row1 = st.columns(3)
row2 = st.columns(3)
for col, (icon, title, desc) in zip(row1 + row2, topics):
    with col:
        st.markdown(
            f"""
            <div style="background:#ffffff;border-radius:12px;
                        padding:1.2rem 1.2rem;margin-bottom:0.75rem;
                        box-shadow:0 2px 10px rgba(0,0,0,0.2);">
                <div style="font-size:1.4rem;margin-bottom:0.5rem;">{icon}</div>
                <div style="font-weight:600;color:#b45309;font-size:0.93rem;
                            margin-bottom:0.3rem;">{title}</div>
                <div style="color:#9b9488;font-size:0.83rem;line-height:1.55;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ── Data pipeline note ────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:#ffffff;border-radius:12px;
                padding:1.2rem 1.4rem;display:flex;gap:1rem;align-items:flex-start;
                box-shadow:0 2px 10px rgba(0,0,0,0.2);">
        <div style="font-size:1.3rem;margin-top:0.1rem;">🔄</div>
        <div>
            <div style="font-weight:700;color:#b45309;margin-bottom:0.2rem;">Live Data Pipeline</div>
            <div style="color:#9b9488;font-size:0.9rem;line-height:1.6;">
                Data is pulled directly from the NYC Open Data API, stored in Google BigQuery,
                and cached for one hour. Each page queries BigQuery in real time — no static snapshots.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Source: NYC Open Data — Motor Vehicle Collisions (Person & Crash) · Updated hourly via BigQuery")