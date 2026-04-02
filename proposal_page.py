import streamlit as st

st.markdown(
    '<span class="page-label">Project 1 · Part 1</span>', unsafe_allow_html=True
)
st.markdown(
    "<h1 style='font-family:Lora,serif;font-weight:400;font-size:2.2rem;"
    "color:#b45309;margin-bottom:0.3rem;'>Research Proposal</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#6a6258;font-size:0.97rem;margin-bottom:1rem;'>"
    "Group <strong style='color:#c9c4bc;'>sparkly-pickle</strong> · Yiran Ge · Yizi Qu</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── 1. Dataset ────────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;color:#b45309;'>1. Dataset</h3>",
    unsafe_allow_html=True,
)

for label, name, desc in [
    (
        "Primary Dataset",
        "Motor Vehicle Collisions – Person Data",
        "This dataset records individuals involved in New York City police-reported motor vehicle "
        "collisions. Each row represents one person involved in a crash (e.g., driver, passenger, "
        "pedestrian, or bicyclist). The dataset includes information on injury severity and road "
        "user type. The data is available starting from 2016, when NYC transitioned to an "
        "electronic crash reporting system.",
    ),
    (
        "Secondary Dataset (merged)",
        "Motor Vehicle Collisions – Crashes",
        "Crash-level records including borough, coordinates, and contributing factors. "
        "Merged with the Person dataset to enable borough-level and GIS-based analysis.",
    ),
]:
    st.markdown(
        f"""
        <div style="background:#1a1c27;border:1px solid #2a2a3a;border-radius:10px;
                    padding:1.1rem 1.3rem;margin-bottom:0.65rem;">
            <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                        color:#b45309;font-weight:600;margin-bottom:0.3rem;">{label}</div>
            <div style="color:#e8e0d4;font-weight:600;font-size:1rem;margin-bottom:0.3rem;">{name}</div>
            <div style="color:#7a7060;font-size:0.9rem;line-height:1.65;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 2. Research Questions ─────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;color:#b45309;'>2. Research Questions</h3>",
    unsafe_allow_html=True,
)

for num, title, body in [
    (
        "1.",
        "Road User Outcomes",
        "How do injury and fatality outcomes differ across types of road users (pedestrians, cyclists, "
        "and motor vehicle occupants) in New York City since 2025?",
    ),
    (
        "2.",
        "Borough Geography",
        "Are there differences in the distribution of traffic-related injuries and fatalities across "
        "NYC boroughs since 2025? This question requires merging the Person dataset with the Motor "
        "Vehicle Collisions – Crashes dataset, which contains detailed location information, enabling "
        "borough-level and GIS-based analysis.",
    ),
    (
        "3.",
        "Temporal Patterns",
        "Do traffic-related injuries and fatalities exhibit temporal patterns over time (e.g., monthly "
        "trends) in New York City since 2025?",
    ),
]:
    st.markdown(
        f"""
        <div style="background:#1a1c27;border:1px solid #2a2a3a;border-radius:10px;
                    padding:1rem 1.3rem;margin-bottom:0.65rem;">
            <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                <div style="font-family:'Lora',serif;font-size:1.4rem;
                            color:#b45309;min-width:1.8rem;">{num}</div>
                <div>
                    <div style="font-weight:600;color:#e8e0d4;margin-bottom:0.2rem;">{title}</div>
                    <div style="color:#7a7060;font-size:0.92rem;line-height:1.65;">{body}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 3. Notebook Link ──────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;color:#b45309;'>3. Notebook Link</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<a href='https://colab.research.google.com/drive/1WEt7ZzIXHlwosCxOBvZGz_kDVjV4zd7u' "
    "target='_blank' style='color:#6b9fd4;font-size:0.95rem;'>"
    "https://colab.research.google.com/drive/1WEt7ZzIXHlwosCxOBvZGz_kDVjV4zd7u</a>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── 4. Target Visualizations ──────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;color:#b45309;'>4. Target Visualizations</h3>",
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
for col, (label, vtype, desc) in zip(
    [c1, c2],
    [
        (
            "Visualization 1",
            "Stacked bar chart",
            "A stacked bar chart comparing counts of injured versus killed individuals by road user type "
            "(pedestrian, cyclist, motor vehicle occupant). The visualization highlights differences in "
            "both total counts and outcome composition for each group since 2025.",
        ),
        (
            "Visualization 2 (Planned)",
            "Faceted monthly time-series (line chart) by borough",
            "This visualization will display monthly counts of injuries and fatalities across NYC boroughs "
            "since 2025 after merging the Person and Crashes datasets. The goal is to identify temporal "
            "patterns, seasonal effects, spikes, and borough-level differences.",
        ),
    ],
):
    with col:
        st.markdown(
            f"""
            <div style="background:#1a1c27;border:1px solid #2a2a3a;border-radius:10px;
                        padding:1.1rem 1.3rem;height:100%;">
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                            color:#b45309;font-weight:600;margin-bottom:0.3rem;">{label}</div>
                <div style="font-weight:600;color:#e8e0d4;margin-bottom:0.3rem;">Type: {vtype}</div>
                <div style="color:#7a7060;font-size:0.88rem;line-height:1.6;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── 5. Known Unknowns ─────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;color:#b45309;'>5. Known Unknowns</h3>",
    unsafe_allow_html=True,
)
for item in [
    "Not all person-level records may link cleanly to crash-level records, which could reduce the usable sample size for borough-level or GIS analyses.",
    "Some crash records may contain missing or incomplete location information, limiting mapping coverage.",
    "The datasets are based on police-reported crashes; underreporting or inconsistencies may exist depending on crash severity and reporting practices.",
]:
    st.markdown(
        f"<div style='display:flex;gap:0.7rem;margin-bottom:0.5rem;'>"
        f"<div style='color:#b45309;margin-top:0.3rem;font-size:0.7rem;'>●</div>"
        f"<div style='color:#7a7060;font-size:0.92rem;line-height:1.65;'>{item}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 6. Anticipated Challenges ─────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:400;color:#b45309;'>6. Anticipated Challenges</h3>",
    unsafe_allow_html=True,
)
for item in [
    "Since the analysis focuses on data from 2025 onward, careful cleaning and standardization of date fields are required to ensure accurate monthly comparisons.",
    "Merging the person-level dataset with the crash-level dataset introduces a risk of double-counting; therefore, the merge process must be handled carefully to maintain consistency and data integrity.",
]:
    st.markdown(
        f"<div style='display:flex;gap:0.7rem;margin-bottom:0.5rem;'>"
        f"<div style='color:#b45309;margin-top:0.3rem;font-size:0.7rem;'>●</div>"
        f"<div style='color:#7a7060;font-size:0.92rem;line-height:1.65;'>{item}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
