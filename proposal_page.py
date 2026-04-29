import streamlit as st

st.markdown(
    '<span class="page-label">Project 1 · Part 1</span>', unsafe_allow_html=True
)
st.markdown(
    "<h1 style='font-family:JetBrains Mono,monospace;font-weight:600;font-size:2.1rem;"
    "color:#0F172A;margin-bottom:0.3rem;letter-spacing:-0.02em;'>Research Proposal</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#64748B;font-size:0.97rem;margin-bottom:1.2rem;'>"
    "Group <strong style='color:#1c2536;'>sparkly-pickle</strong> · Yiran Ge · Yizi Qu</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── 1. Dataset ────────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "1. Dataset</h3>",
    unsafe_allow_html=True,
)

for label, name, desc in [
    (
        "Primary Dataset",
        "Motor Vehicle Collisions – Person Data",
        "Each row represents one person involved in an NYC police-reported crash — driver, "
        "passenger, pedestrian, or cyclist. Includes injury severity, person type, and safety "
        "equipment used. Available since 2016 when NYC moved to electronic crash reporting.",
    ),
    (
        "Secondary Dataset (merged)",
        "Motor Vehicle Collisions – Crashes",
        "Crash-level records including borough, coordinates, time of day, and contributing factors. "
        "Merged with the Person dataset to connect cause (what triggered the crash) with outcome "
        "(who was hurt, how badly, and where).",
    ),
]:
    st.markdown(
        f"""
        <div class="card">
            <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                        color:#4A7FB5;font-weight:700;margin-bottom:0.3rem;">{label}</div>
            <div style="color:#0F172A;font-weight:600;font-size:1rem;margin-bottom:0.4rem;
                        font-family:JetBrains Mono,monospace;">{name}</div>
            <div style="color:#475569;font-size:0.9rem;line-height:1.7;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 2. Research Questions ─────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "2. Research Questions &amp; Hypotheses</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.75;margin-bottom:1rem;'>"
    "Each question below is built around a specific hypothesis that our two datasets can directly test. "
    "The shared argument across all three is that NYC's traffic safety problem looks very different "
    "depending on where you are and what time it is — and that a one-size-fits-all policy response "
    "will miss the places and moments where the risk is actually highest.</p>",
    unsafe_allow_html=True,
)

for num, title, body, hypothesis in [
    (
        "1.",
        "Do crash causes vary by borough — and does the same cause lead to worse outcomes in some areas?",
        "We know that driver inattention is the most common crash cause city-wide. But is that "
        "true in every borough, or do some areas have a very different mix of causes? And if the "
        "same cause — say, distracted driving — shows up in multiple boroughs, does it lead to "
        "more deaths and injuries in some boroughs than others? We expect the answer to both "
        "questions to be yes, because road design, speed limits, and pedestrian density vary "
        "significantly across the five boroughs.",
        "If crash causes differ by borough, then the city should set borough-level enforcement "
        "priorities rather than running the same campaigns everywhere. And if the same cause "
        "is more deadly in certain boroughs, those areas likely need physical road changes — "
        "not just more enforcement — to bring outcomes in line with the rest of the city.",
    ),
    (
        "2.",
        "Do crash causes look different at night compared to during the day?",
        "Rush hour produces the most crashes by volume, but we expect that late-night crashes "
        "(10 pm to 3 am, especially on weekends) are caused by a different mix of factors — "
        "with a higher share coming from speeding and impaired driving compared to daytime "
        "crashes, which are more likely to involve distraction and failure to yield. "
        "If the cause profile shifts significantly between day and night, it means the two "
        "time windows are essentially different problems that need different responses.",
        "A city that deploys the same enforcement strategy around the clock is likely "
        "over-investing during the day and under-investing at night. If late-night crashes "
        "have a different cause mix, traffic resources — cameras, patrols, and public "
        "messaging — should be adjusted by time of day, not just by location.",
    ),
    (
        "3.",
        "Which boroughs are most dangerous for pedestrians specifically — and is that different from total crash rankings?",
        "Brooklyn and Queens top the city in total crash counts. But we want to know whether "
        "they also have the highest share of pedestrian deaths — or whether a different borough "
        "is actually the most dangerous place to walk. We expect the pedestrian death ranking "
        "to differ from the total crash ranking, because pedestrian risk depends more on "
        "street design and vehicle speed than on overall traffic volume.",
        "If the boroughs with the most pedestrian deaths are not the same as the ones with "
        "the most total crashes, then allocating pedestrian safety budgets based on crash "
        "volume alone will send money to the wrong places. Resources like protected crossings, "
        "pedestrian signals, and traffic calming should follow the pedestrian death share, "
        "not the headline crash numbers.",
    ),
]:
    st.markdown(
        f"""
        <div class="card">
            <div style="display:flex;gap:0.85rem;align-items:flex-start;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;
                            color:#6F9FCF;min-width:1.8rem;font-weight:700;">{num}</div>
                <div style="width:100%;">
                    <div style="font-weight:700;color:#0F172A;margin-bottom:0.4rem;
                                font-family:'JetBrains Mono',monospace;font-size:1rem;
                                line-height:1.4;">{title}</div>
                    <div style="color:#475569;font-size:0.92rem;line-height:1.7;margin-bottom:0.7rem;">{body}</div>
                    <div style="background:#F0F6FB;border-left:3px solid #4A7FB5;border-radius:0 6px 6px 0;
                                padding:0.7rem 1rem;color:#334155;font-size:0.88rem;line-height:1.7;">
                        <strong style="color:#4A7FB5;">Hypothesis &amp; Policy Relevance</strong><br>{hypothesis}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 3. Refined Scope ──────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "3. Refined Scope &amp; Analytical Approach</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
        <div style="color:#0F172A;font-weight:700;font-size:0.97rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">The central argument</div>
        <div style="color:#475569;font-size:0.91rem;line-height:1.75;">
            NYC's traffic safety problem is not uniform. The same city-wide statistics that show
            driver inattention as the top cause hide the fact that crash causes, severity, and
            victim profiles look very different depending on which borough you are in and what
            time of day it is. A policy that treats all boroughs and all hours the same will
            systematically under-serve the places and moments where the risk is actually highest.
        </div>
    </div>
    <div class="card">
        <div style="color:#0F172A;font-weight:700;font-size:0.97rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">Why these two datasets together</div>
        <div style="color:#475569;font-size:0.91rem;line-height:1.75;">
            The Crash table tells us where, when, and why each collision happened. The Person table
            tells us who was hurt and how badly. Neither dataset alone can answer our questions —
            we need to merge them to connect cause (what triggered the crash) with outcome
            (who died, and where). This merge is what allows us to go beyond counting crashes
            and ask whether the same cause is more deadly in some boroughs than others,
            and whether pedestrian deaths are concentrated in the same places as total crashes.
        </div>
    </div>
    <div class="card">
        <div style="color:#0F172A;font-weight:700;font-size:0.97rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">What "precision policy" means here</div>
        <div style="color:#475569;font-size:0.91rem;line-height:1.75;">
            Our findings are intended to support a shift from city-wide uniform interventions
            toward borough-level and time-of-day-specific ones. Concretely: each borough setting
            its own enforcement priority based on its dominant crash cause, late-night resources
            being deployed differently from daytime ones, and pedestrian safety budgets following
            pedestrian death share rather than total crash volume.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── 4. Notebook Link ──────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "4. Notebook Link</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<a href='https://colab.research.google.com/drive/1WEt7ZzIXHlwosCxOBvZGz_kDVjV4zd7u' "
    "target='_blank' style='color:#4A7FB5;font-size:0.95rem;'>"
    "https://colab.research.google.com/drive/1WEt7ZzIXHlwosCxOBvZGz_kDVjV4zd7u</a>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── 5. Known Unknowns ─────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "5. Known Unknowns</h3>",
    unsafe_allow_html=True,
)
for item in [
    "Not all person-level records may link cleanly to crash-level records, which could reduce the usable sample size for borough-level or GIS analyses.",
    "Some crash records may contain missing or incomplete location information, limiting mapping coverage.",
    "The datasets are based on police-reported crashes; underreporting or inconsistencies may exist depending on crash severity and reporting practices.",
    "Contributing factor data is recorded by responding officers and reflects their judgment at the scene — categories like 'driver inattention' may absorb cases that more nuanced reporting would distinguish.",
]:
    st.markdown(
        f"<div style='display:flex;gap:0.7rem;margin-bottom:0.55rem;'>"
        f"<div style='color:#6F9FCF;margin-top:0.35rem;font-size:0.7rem;'>●</div>"
        f"<div style='color:#475569;font-size:0.92rem;line-height:1.7;'>{item}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── 6. Anticipated Challenges ─────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "6. Anticipated Challenges</h3>",
    unsafe_allow_html=True,
)
for item in [
    "Since the analysis focuses on data from 2025 onward, careful cleaning and standardization of date fields are required to ensure accurate monthly comparisons.",
    "Merging the person-level dataset with the crash-level dataset introduces a risk of double-counting; the merge process must be handled carefully to maintain consistency and data integrity.",
    "Comparing crash causes across boroughs requires accurate denominators (total crashes per borough). Smaller boroughs like Staten Island may produce noisier rates that should be flagged in the visualizations.",
]:
    st.markdown(
        f"<div style='display:flex;gap:0.7rem;margin-bottom:0.55rem;'>"
        f"<div style='color:#6F9FCF;margin-top:0.35rem;font-size:0.7rem;'>●</div>"
        f"<div style='color:#475569;font-size:0.92rem;line-height:1.7;'>{item}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
