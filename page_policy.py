"""
Page 4 — Policy Levers.

Synthesizes the findings from Modules 1–3 into specific, evidence-backed
recommendations. Each lever is tied to the data finding that justifies it
and the borough/time/group it targets.
"""

import time
from concurrent.futures import ThreadPoolExecutor

import altair as alt
import pandas as pd
import streamlit as st
from google.cloud import bigquery as bq

from filters import render_filters, render_context_bar
from shared import (
    get_bigquery_client,
    formula_box,
    takeaway,
    SIPA_BLUE,
    ACCENT_RED,
)

start_time = time.time()

# ── Sidebar filters ──────────────────────────────────────────────────────────
filters = render_filters()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-label">Module 4 · Policy Synthesis</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-family:JetBrains Mono,monospace;font-weight:600;font-size:2rem;"
    "color:#0F172A;margin-bottom:0.3rem;letter-spacing:-0.02em;'>Policy Levers</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.97rem;line-height:1.7;margin-bottom:1rem;'>"
    "The previous three modules established the diagnosis. This module translates that diagnosis "
    "into specific levers — each tied to a finding from the data and a population it serves. "
    "The unifying claim: precision policy outperforms uniform policy because the underlying "
    "problem is itself heterogeneous.</p>",
    unsafe_allow_html=True,
)

render_context_bar("Synthesis & policy recommendations", filters)


# ── Load lightweight data for the recommendations ────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_top_cause_per_borough(date_start, date_end):
    query = """
    WITH classified AS (
        SELECT
            INITCAP(borough) AS borough,
            CASE
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%inattention%' THEN 'Driver inattention/distraction'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%distract%'    THEN 'Driver inattention/distraction'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%failure to yield%' THEN 'Failure to yield'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%following too closely%' THEN 'Following too closely'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%passing or lane%' THEN 'Improper passing/lane use'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%speed%'        THEN 'Unsafe speed'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%alcohol%'      THEN 'Alcohol involvement'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%traffic control disregarded%' THEN 'Disregard of traffic control'
                ELSE 'Other'
            END AS cause
        FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
        WHERE EXTRACT(YEAR FROM crash_date) = 2026
          AND DATE(crash_date) BETWEEN @date_start AND @date_end
          AND borough IS NOT NULL AND TRIM(borough) != ''
          AND contributing_factor_vehicle_1 IS NOT NULL
          AND LOWER(contributing_factor_vehicle_1) NOT IN ('unspecified', '')
    ),
    counts AS (
        SELECT borough, cause, COUNT(*) AS crashes
        FROM classified
        WHERE cause != 'Other'
        GROUP BY borough, cause
    ),
    ranked AS (
        SELECT
            borough, cause, crashes,
            RANK() OVER (PARTITION BY borough ORDER BY crashes DESC) AS rk,
            SUM(crashes) OVER (PARTITION BY borough) AS borough_total
        FROM counts
    )
    SELECT borough, cause, crashes, ROUND(crashes / borough_total * 100, 1) AS share
    FROM ranked
    WHERE rk = 1
    ORDER BY crashes DESC
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end", "DATE", date_end),
        ]
    )
    return (
        get_bigquery_client()
        .query(query, job_config=job_config)
        .to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_pedestrian_priority(date_start, date_end):
    query = """
    SELECT
        INITCAP(borough)                  AS borough,
        COUNT(*)                          AS crashes,
        SUM(number_of_persons_killed)     AS total_killed,
        SUM(number_of_pedestrians_killed) AS pedestrians_killed
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
      AND DATE(crash_date) BETWEEN @date_start AND @date_end
      AND borough IS NOT NULL AND TRIM(borough) != ''
    GROUP BY borough
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end", "DATE", date_end),
        ]
    )
    return (
        get_bigquery_client()
        .query(query, job_config=job_config)
        .to_dataframe(create_bqstorage_client=False)
    )


with st.spinner("Loading synthesis data..."):
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_top = pool.submit(
            load_top_cause_per_borough, filters["date_start"], filters["date_end"]
        )
        f_ped = pool.submit(
            load_pedestrian_priority, filters["date_start"], filters["date_end"]
        )
    top_cause_df = f_top.result()
    ped_priority_df = f_ped.result()

# ── Lever 1: Borough-Level Enforcement Priorities ────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Lever 1 — Set borough-specific enforcement priorities</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
        <div style="display:flex;gap:0.6rem;align-items:center;margin-bottom:0.6rem;">
            <span class="status-warning">Borough-targeted</span>
            <span style="color:#64748B;font-size:0.82rem;">Source finding: Module 3 · RQ1</span>
        </div>
        <div style="color:#0F172A;font-weight:600;font-size:0.97rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">The argument</div>
        <div style="color:#475569;font-size:0.91rem;line-height:1.7;margin-bottom:0.6rem;">
            Module 3 showed that crash cause profiles are not the same across boroughs. Each borough's
            top-priority cause should drive its enforcement focus, instead of a citywide campaign that
            treats every borough's problem as identical.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not top_cause_df.empty:
    st.markdown(
        "<div style='font-family:JetBrains Mono,monospace;font-size:0.85rem;color:#64748B;"
        "margin:0.6rem 0;text-transform:uppercase;letter-spacing:0.1em;'>"
        "What the data says — top crash cause by borough</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(min(len(top_cause_df), 5))
    for col, (_, row) in zip(cols, top_cause_df.iterrows()):
        col.markdown(
            f"""
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;
                        padding:1rem 1rem;height:100%;
                        box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                            color:#4A7FB5;font-weight:700;margin-bottom:0.4rem;">{row["borough"]}</div>
                <div style="font-weight:600;color:#0F172A;font-size:0.92rem;
                            line-height:1.35;margin-bottom:0.4rem;
                            font-family:JetBrains Mono,monospace;">{row["cause"]}</div>
                <div style="color:#64748B;font-size:0.78rem;">
                    {row["share"]:.1f}% of crashes · {int(row["crashes"]):,} incidents
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

formula_box(
    "Calculation",
    "Top Cause (borough) = argmax_cause [ Crashes(borough, cause) ÷ Crashes(borough) × 100 ]",
    "For each borough, identify the cause with the highest share of that borough's crashes. "
    "Resources should be allocated proportional to local cause prevalence — not the citywide average.",
)

st.markdown(
    """
    <div class="card">
        <div style="color:#0F172A;font-weight:600;font-size:0.95rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">Concrete recommendations</div>
        <ul style="color:#475569;font-size:0.9rem;line-height:1.85;margin:0;padding-left:1.2rem;">
            <li>NYPD precincts run public-messaging campaigns matched to their borough's top cause —
                not a uniform citywide message.</li>
            <li>Speed-camera and red-light-camera deployment plans rebalanced to match the dominant
                cause in each borough's crash data.</li>
            <li>Annual borough-level "cause score card" published so progress is measurable
                against each borough's own baseline.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Lever 2: Time-of-Day Resource Reallocation ───────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Lever 2 — Reallocate enforcement resources by time of day</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
        <div style="display:flex;gap:0.6rem;align-items:center;margin-bottom:0.6rem;">
            <span class="status-warning">Time-targeted</span>
            <span style="color:#64748B;font-size:0.82rem;">Source finding: Module 3 · RQ2</span>
        </div>
        <div style="color:#0F172A;font-weight:600;font-size:0.97rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">The argument</div>
        <div style="color:#475569;font-size:0.91rem;line-height:1.7;margin-bottom:0.6rem;">
            Late-night crashes draw a higher share from speeding and alcohol than daytime crashes,
            which lean on distraction and failure to yield. The right enforcement tool changes
            with the time window — running the same approach 24/7 wastes effort during the day
            and under-resources the most dangerous hours of the night.
        </div>
        <div style="color:#0F172A;font-weight:600;font-size:0.95rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">Concrete recommendations</div>
        <ul style="color:#475569;font-size:0.9rem;line-height:1.85;margin:0;padding-left:1.2rem;">
            <li>Daytime: focus on automated distraction-detection cameras and rear-end-collision
                hotspot enforcement, where failure to yield and following too closely dominate.</li>
            <li>Late night (10pm–6am, Friday/Saturday especially): shift to DWI checkpoints,
                speed-camera operations, and high-visibility patrols on arterials known for
                high-speed crashes.</li>
            <li>Public messaging time-keyed: morning commute messaging targets phone use; nightlife
                area messaging targets impairment and ride-share use.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

formula_box(
    "Calculation",
    "Cause Imbalance = | Cause Share (night) − Cause Share (day) |",
    "The bigger the gap between day and night for a given cause, the stronger the case for "
    "time-segmented enforcement. Causes with near-zero gaps can keep uniform deployment.",
)

st.markdown("---")

# ── Lever 3: Pedestrian-First Budget Allocation ──────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Lever 3 — Allocate pedestrian safety budgets by death share, not crash volume</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
        <div style="display:flex;gap:0.6rem;align-items:center;margin-bottom:0.6rem;">
            <span class="status-critical">Equity-critical</span>
            <span style="color:#64748B;font-size:0.82rem;">Source finding: Module 2 + Module 3 · RQ3</span>
        </div>
        <div style="color:#0F172A;font-weight:600;font-size:0.97rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">The argument</div>
        <div style="color:#475569;font-size:0.91rem;line-height:1.7;margin-bottom:0.6rem;">
            Module 2 showed pedestrians die at multiples of their crash-involvement share.
            Module 3 showed that the boroughs with the most pedestrian deaths are not necessarily
            the boroughs with the most total crashes. Funding pedestrian safety by total crash
            volume sends the right amount of money to the wrong boroughs.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not ped_priority_df.empty:
    ped_priority_df = ped_priority_df.copy()
    ped_priority_df["ped_death_share"] = (
        (
            ped_priority_df["pedestrians_killed"]
            / ped_priority_df["total_killed"].replace(0, pd.NA)
            * 100
        )
        .fillna(0)
        .round(1)
    )
    ped_priority_df["crash_share"] = (
        ped_priority_df["crashes"] / ped_priority_df["crashes"].sum() * 100
    ).round(1)
    ped_priority_df["allocation_gap"] = (
        ped_priority_df["ped_death_share"] - ped_priority_df["crash_share"]
    ).round(1)

    st.markdown(
        "<div style='font-family:JetBrains Mono,monospace;font-size:0.85rem;color:#64748B;"
        "margin:0.6rem 0;text-transform:uppercase;letter-spacing:0.1em;'>"
        "Allocation gap — pedestrian death share minus crash volume share</div>",
        unsafe_allow_html=True,
    )

    melted = ped_priority_df.melt(
        id_vars="borough",
        value_vars=["crash_share", "ped_death_share"],
        var_name="metric",
        value_name="share",
    )
    metric_label_map = {
        "crash_share": "Crash volume share",
        "ped_death_share": "Pedestrian death share",
    }
    melted["metric"] = melted["metric"].map(metric_label_map)

    chart = (
        alt.Chart(melted)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("share:Q", title="Share (%)"),
            y=alt.Y("borough:N", sort="-x", title=None),
            color=alt.Color(
                "metric:N",
                scale=alt.Scale(
                    domain=["Crash volume share", "Pedestrian death share"],
                    range=[SIPA_BLUE, ACCENT_RED],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            yOffset=alt.YOffset("metric:N"),
            tooltip=[
                alt.Tooltip("borough:N", title="Borough"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("share:Q", title="Share", format=".1f"),
            ],
        )
        .properties(height=260)
    )

    st.altair_chart(chart, use_container_width=True)

    formula_box(
        "Allocation Gap (per borough)",
        "Gap = Pedestrian Death Share % − Crash Volume Share %",
        "A positive gap means the borough is currently under-funded for pedestrian safety relative to "
        "the harm pedestrians experience there. A negative gap means current allocations may be "
        "over-weighted relative to actual pedestrian risk.",
    )

    # Surface the boroughs with the largest positive and negative gaps
    underfunded = ped_priority_df.sort_values("allocation_gap", ascending=False).head(2)
    if not underfunded.empty:
        rows_html = "".join(
            f"<li><strong style='color:#0F172A;'>{r['borough']}</strong>: "
            f"{r['ped_death_share']:.1f}% of pedestrian deaths but only {r['crash_share']:.1f}% of "
            f"total crashes — a gap of <strong style='color:#B91C1C;'>+{r['allocation_gap']:.1f} "
            f"percentage points</strong>. Pedestrian safety budgets here likely under-resourced.</li>"
            for _, r in underfunded.iterrows()
            if r["allocation_gap"] > 0
        )
        if rows_html:
            st.markdown(
                f"""
                <div class="card">
                    <div style="color:#0F172A;font-weight:600;font-size:0.95rem;margin-bottom:0.5rem;
                                font-family:JetBrains Mono,monospace;">Boroughs with the biggest allocation gap</div>
                    <ul style="color:#475569;font-size:0.9rem;line-height:1.85;margin:0;padding-left:1.2rem;">
                        {rows_html}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown(
    """
    <div class="card">
        <div style="color:#0F172A;font-weight:600;font-size:0.95rem;margin-bottom:0.5rem;
                    font-family:JetBrains Mono,monospace;">Concrete recommendations</div>
        <ul style="color:#475569;font-size:0.9rem;line-height:1.85;margin:0;padding-left:1.2rem;">
            <li>Pedestrian-safety capital budget (protected crossings, leading-pedestrian intervals,
                curb extensions) reallocated based on each borough's pedestrian death share — not
                its total crash count.</li>
            <li>Borough-by-borough pedestrian fatality dashboard, refreshed monthly, with public
                threshold triggers that activate immediate street-safety audits.</li>
            <li>Speed-limit reductions on arterials in boroughs with the highest pedestrian death
                share, paired with engineering changes (raised crosswalks, daylighting) to enforce
                the new limit physically rather than only legally.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Final synthesis ──────────────────────────────────────────────────────────
takeaway(
    "<strong style='color:#1c2536;'>The unifying claim:</strong> NYC traffic safety is not one "
    "problem with one solution. It is at least three overlapping problems — "
    "<em>cause heterogeneity across boroughs</em>, <em>cause heterogeneity across time of day</em>, "
    "and <em>burden inequality across road user types</em>. Each demands its own lever.<br><br>"
    "<strong style='color:#1c2536;'>Why this matters in practice:</strong> Uniform city-wide "
    "policies are politically simpler but operationally inefficient — they over-fund areas where "
    "the marginal return is low and under-fund areas where it would be high. The data-supported "
    "alternative is precision policy: borough-specific causes, time-specific tactics, "
    "pedestrian-specific budgets.<br><br>"
    "<strong style='color:#1c2536;'>Limits we acknowledge:</strong> Police-recorded contributing "
    "factors reflect officer judgment at the scene. Pedestrian death counts in smaller boroughs "
    "are noisy. Causation cannot be established from observational data alone. None of this "
    "invalidates the directional finding, but it argues for treating these recommendations as "
    "starting points for further investigation rather than final prescriptions.",
    label="📌 Synthesis: From Diagnosis to Action",
)

elapsed = time.time() - start_time
st.caption(f"Loaded in {elapsed:.2f}s")
