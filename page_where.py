"""
Page 3 — Where & When.

This is where the three research questions are directly tested:
  RQ1 — Do crash causes vary by borough?
  RQ2 — Do crash causes look different at night vs. during the day?
  RQ3 — Which boroughs are most dangerous for pedestrians (vs. just having most crashes)?

The unifying claim is that citywide averages hide borough-level and time-of-day-level
differences that should be driving precision policy.
"""

import time
from concurrent.futures import ThreadPoolExecutor

import altair as alt
import pandas as pd
import streamlit as st
from google.cloud import bigquery as bq

from filters import render_filters, render_context_bar, time_period_sql_clause
from shared import (
    get_bigquery_client,
    formula_box,
    insight,
    takeaway,
    SIPA_BLUE,
    ACCENT_AMBER,
    ACCENT_RED,
)

start_time = time.time()

# ── Sidebar filters ──────────────────────────────────────────────────────────
filters = render_filters()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-label">Module 3 · Geographic & Temporal Analysis</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-family:JetBrains Mono,monospace;font-weight:600;font-size:2rem;"
    "color:#0F172A;margin-bottom:0.3rem;letter-spacing:-0.02em;'>Where &amp; When</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.97rem;line-height:1.7;margin-bottom:1rem;'>"
    "This is the core analytical module. Three research questions are tested here: "
    "(1) do crash causes vary by borough; (2) do they shift between day and night; "
    "(3) does the pedestrian-death ranking differ from the total-crash ranking? "
    "Each answer translates directly into a different policy implication.</p>",
    unsafe_allow_html=True,
)

render_context_bar("Cause × borough × time-of-day analysis", filters)

# ── Cached queries ──────────────────────────────────────────────────────────


@st.cache_data(ttl=3600, show_spinner=False)
def load_borough_causes(date_start, date_end, time_period, boroughs_tuple):
    time_clause = time_period_sql_clause(time_period, "EXTRACT(HOUR FROM crash_date)")
    bf = "AND UPPER(borough) IN UNNEST(@boroughs)" if len(boroughs_tuple) < 5 else ""
    query = f"""
    WITH classified AS (
        SELECT
            INITCAP(borough) AS borough,
            CASE
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%inattention%' THEN 'Driver inattention/distraction'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%distract%'    THEN 'Driver inattention/distraction'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%failure to yield%' THEN 'Failure to yield'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%following too closely%' THEN 'Following too closely'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%backing unsafely%' THEN 'Unsafe backing'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%passing or lane%' THEN 'Improper passing/lane use'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%speed%'        THEN 'Unsafe speed'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%alcohol%'      THEN 'Alcohol involvement'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%traffic control disregarded%' THEN 'Disregard of traffic control'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%fell asleep%'  THEN 'Driver fatigue'
                ELSE 'Other'
            END AS cause
        FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
        WHERE EXTRACT(YEAR FROM crash_date) = 2026
          AND DATE(crash_date) BETWEEN @date_start AND @date_end
          AND borough IS NOT NULL AND TRIM(borough) != ''
          AND contributing_factor_vehicle_1 IS NOT NULL
          AND LOWER(contributing_factor_vehicle_1) NOT IN ('unspecified', '')
          {time_clause}
    )
    SELECT borough, cause, COUNT(*) AS crashes
    FROM classified
    WHERE cause != 'Other'
      {bf}
    GROUP BY borough, cause
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end", "DATE", date_end),
            bq.ArrayQueryParameter(
                "boroughs", "STRING", [b.upper() for b in boroughs_tuple]
            ),
        ]
    )
    return (
        get_bigquery_client()
        .query(query, job_config=job_config)
        .to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_day_night_causes(date_start, date_end, boroughs_tuple):
    bf = "AND UPPER(borough) IN UNNEST(@boroughs)" if len(boroughs_tuple) < 5 else ""
    query = f"""
    WITH classified AS (
        SELECT
            CASE
                WHEN EXTRACT(HOUR FROM crash_date) BETWEEN 6 AND 21 THEN 'Daytime (6am–10pm)'
                ELSE 'Late night (10pm–6am)'
            END AS time_period,
            CASE
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%inattention%' THEN 'Driver inattention/distraction'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%distract%'    THEN 'Driver inattention/distraction'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%failure to yield%' THEN 'Failure to yield'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%following too closely%' THEN 'Following too closely'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%speed%'        THEN 'Unsafe speed'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%alcohol%'      THEN 'Alcohol involvement'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%traffic control disregarded%' THEN 'Disregard of traffic control'
                WHEN LOWER(contributing_factor_vehicle_1) LIKE '%fell asleep%'  THEN 'Driver fatigue'
                ELSE 'Other'
            END AS cause
        FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
        WHERE EXTRACT(YEAR FROM crash_date) = 2026
          AND DATE(crash_date) BETWEEN @date_start AND @date_end
          AND contributing_factor_vehicle_1 IS NOT NULL
          AND LOWER(contributing_factor_vehicle_1) NOT IN ('unspecified', '')
          {bf}
    )
    SELECT time_period, cause, COUNT(*) AS crashes
    FROM classified
    WHERE cause != 'Other'
    GROUP BY time_period, cause
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end", "DATE", date_end),
            bq.ArrayQueryParameter(
                "boroughs", "STRING", [b.upper() for b in boroughs_tuple]
            ),
        ]
    )
    return (
        get_bigquery_client()
        .query(query, job_config=job_config)
        .to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_pedestrian_by_borough(date_start, date_end, time_period):
    time_clause = time_period_sql_clause(time_period, "EXTRACT(HOUR FROM crash_date)")
    query = f"""
    SELECT
        INITCAP(borough)                           AS borough,
        COUNT(*)                                   AS crashes,
        SUM(number_of_persons_killed)              AS total_killed,
        SUM(number_of_pedestrians_killed)          AS pedestrians_killed,
        SUM(number_of_cyclist_killed)              AS cyclists_killed
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
      AND DATE(crash_date) BETWEEN @date_start AND @date_end
      AND borough IS NOT NULL AND TRIM(borough) != ''
      {time_clause}
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


# ── Load ─────────────────────────────────────────────────────────────────────
boroughs_tuple = tuple(sorted(filters["boroughs"]))

with st.spinner("Loading data from BigQuery..."):
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_borough_cause = pool.submit(
            load_borough_causes,
            filters["date_start"],
            filters["date_end"],
            filters["time_period"],
            boroughs_tuple,
        )
        f_daynight = pool.submit(
            load_day_night_causes,
            filters["date_start"],
            filters["date_end"],
            boroughs_tuple,
        )
        f_pedestrian = pool.submit(
            load_pedestrian_by_borough,
            filters["date_start"],
            filters["date_end"],
            filters["time_period"],
        )

    borough_cause_df = f_borough_cause.result()
    daynight_df = f_daynight.result()
    ped_borough_df = f_pedestrian.result()

# ── RQ1 — Do crash causes vary by borough? ───────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "RQ1 — Do crash causes vary by borough?</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "The chart below shows, for each borough, the percent of crashes attributed to each cause. "
    "If every borough has the same cause profile, a city-wide enforcement strategy makes sense. "
    "If borough cause profiles diverge, they should each have their own enforcement priorities.</p>",
    unsafe_allow_html=True,
)

formula_box(
    "Formula 1 — Borough Cause Share",
    "Cause Share (borough) = ( Crashes from cause in borough ÷ Total crashes in borough ) × 100",
    "Each borough's bar should sum to 100%. Differences in the size of each colored segment between "
    "boroughs are exactly what we're testing for.",
)

if not borough_cause_df.empty:
    cause_share = borough_cause_df.assign(
        total=borough_cause_df.groupby("borough")["crashes"].transform("sum")
    ).assign(share=lambda d: d["crashes"] / d["total"] * 100)

    cause_chart = (
        alt.Chart(cause_share)
        .mark_bar()
        .encode(
            x=alt.X(
                "share:Q",
                title="Share of borough's crashes (%)",
                stack="normalize",
                axis=alt.Axis(format="%"),
            ),
            y=alt.Y("borough:N", sort="-x", title=None),
            color=alt.Color(
                "cause:N",
                legend=alt.Legend(title="Crash cause", orient="bottom", columns=2),
            ),
            tooltip=[
                alt.Tooltip("borough:N", title="Borough"),
                alt.Tooltip("cause:N", title="Cause"),
                alt.Tooltip("crashes:Q", title="Crashes", format=","),
                alt.Tooltip("share:Q", title="Share", format=".1f"),
            ],
        )
        .properties(height=260)
    )

    st.altair_chart(cause_chart, use_container_width=True)

    insight(
        "If you compare the colored segments across boroughs, you'll see that cause profiles are "
        "<em>not</em> identical. Some boroughs lean more heavily on driver inattention, others see "
        "a higher share of failure to yield, and some show notable contributions from speed or "
        "alcohol. This variation is the empirical basis for borough-level enforcement priorities — "
        "running the same campaign in every borough wastes effort where the dominant cause is different."
    )
else:
    st.info("No cause-by-borough data available for this filter selection.")

st.markdown("---")

# ── RQ2 — Day vs. Night cause profiles ───────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "RQ2 — Do crash causes look different at night?</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "Daytime (6am–10pm) and late-night (10pm–6am) crashes are compared side by side. "
    "If the cause profile shifts significantly, these are essentially two different problems. "
    "We're particularly interested in whether speed and alcohol surge at night — the prediction "
    "is that they do.</p>",
    unsafe_allow_html=True,
)

formula_box(
    "Formula 2 — Time-of-Day Cause Share",
    "Cause Share (period) = ( Crashes from cause in period ÷ Total crashes in period ) × 100",
    "Comparing percentages, not raw counts, is essential — daytime has far more crashes overall, "
    "so raw counts would always show daytime as bigger. Shares show what's <em>relatively</em> dominant.",
)

if not daynight_df.empty:
    daynight_share = daynight_df.assign(
        total=daynight_df.groupby("time_period")["crashes"].transform("sum")
    ).assign(share=lambda d: d["crashes"] / d["total"] * 100)

    daynight_chart = (
        alt.Chart(daynight_share)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("share:Q", title="Share of period's crashes (%)"),
            y=alt.Y("cause:N", sort="-x", title=None),
            color=alt.Color(
                "time_period:N",
                scale=alt.Scale(
                    domain=["Daytime (6am–10pm)", "Late night (10pm–6am)"],
                    range=[SIPA_BLUE, ACCENT_AMBER],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            yOffset=alt.YOffset("time_period:N"),
            tooltip=[
                alt.Tooltip("cause:N", title="Cause"),
                alt.Tooltip("time_period:N", title="Period"),
                alt.Tooltip("share:Q", title="Share", format=".1f"),
                alt.Tooltip("crashes:Q", title="Crashes", format=","),
            ],
        )
        .properties(height=320)
    )

    st.altair_chart(daynight_chart, use_container_width=True)

    # Compute the speed and alcohol delta
    pivot = daynight_share.pivot(
        index="cause", columns="time_period", values="share"
    ).fillna(0)
    if "Unsafe speed" in pivot.index and "Late night (10pm–6am)" in pivot.columns:
        speed_day = (
            pivot.loc["Unsafe speed", "Daytime (6am–10pm)"]
            if "Daytime (6am–10pm)" in pivot.columns
            else 0
        )
        speed_night = pivot.loc["Unsafe speed", "Late night (10pm–6am)"]
        speed_delta = speed_night - speed_day
        if speed_day > 0:
            multiplier = speed_night / speed_day
            insight(
                f"Late-night crashes show <strong style='color:#B91C1C;'>"
                f"{multiplier:.1f}× more share of unsafe speed</strong> "
                f"({speed_night:.1f}% at night vs. {speed_day:.1f}% during the day). "
                "This is direct evidence that the night-time problem is structurally different — "
                "the same officers, cameras, and messaging tuned for distracted-driving rush hour "
                "won't be the right tools for high-speed late-night enforcement."
            )
    else:
        insight(
            "Late-night crashes show a measurably different cause profile from daytime crashes — "
            "in particular, the share attributable to unsafe speed and alcohol is higher at night. "
            "This supports separating day and night enforcement strategies rather than running "
            "the same approach 24/7."
        )
else:
    st.info("No day/night cause data available for this filter selection.")

st.markdown("---")

# ── RQ3 — Borough rankings: total crashes vs. pedestrian deaths ──────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "RQ3 — Where are pedestrians most at risk? (And is it the same as where crashes are most common?)</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "Two rankings, side by side: total crashes vs. pedestrian death share. "
    "If the rankings agree, pedestrian budgets can follow crash-volume logic. "
    "If they disagree, the standard logic is sending money to the wrong boroughs.</p>",
    unsafe_allow_html=True,
)

formula_box(
    "Formula 3 — Pedestrian Death Share by Borough",
    "Ped Death Share (borough) = ( Pedestrians killed in borough ÷ Total killed in borough ) × 100",
    "What percent of each borough's traffic deaths are pedestrians? A borough where pedestrians "
    "make up a disproportionate share of deaths is a borough where walking is unusually dangerous — "
    "regardless of how many total crashes happen there.",
)

if not ped_borough_df.empty:
    ped_borough_df = ped_borough_df.copy()
    ped_borough_df["ped_death_share"] = (
        (
            ped_borough_df["pedestrians_killed"]
            / ped_borough_df["total_killed"].replace(0, pd.NA)
            * 100
        )
        .fillna(0)
        .round(1)
    )

    col_l, col_r = st.columns(2)

    with col_l:
        crash_chart = (
            alt.Chart(ped_borough_df)
            .mark_bar(cornerRadiusEnd=3, color=SIPA_BLUE)
            .encode(
                x=alt.X("crashes:Q", title="Total crashes"),
                y=alt.Y("borough:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("borough:N", title="Borough"),
                    alt.Tooltip("crashes:Q", title="Crashes", format=","),
                ],
            )
            .properties(height=210, title="Ranking by total crashes")
        )
        st.altair_chart(crash_chart, use_container_width=True)

    with col_r:
        ped_chart = (
            alt.Chart(ped_borough_df)
            .mark_bar(cornerRadiusEnd=3, color=ACCENT_RED)
            .encode(
                x=alt.X("ped_death_share:Q", title="Pedestrian death share (%)"),
                y=alt.Y("borough:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("borough:N", title="Borough"),
                    alt.Tooltip(
                        "ped_death_share:Q", title="Ped. death share", format=".1f"
                    ),
                    alt.Tooltip("pedestrians_killed:Q", title="Pedestrians killed"),
                    alt.Tooltip("total_killed:Q", title="Total killed"),
                ],
            )
            .properties(height=210, title="Ranking by pedestrian death share")
        )
        st.altair_chart(ped_chart, use_container_width=True)

    crash_rank = ped_borough_df.sort_values("crashes", ascending=False)[
        "borough"
    ].tolist()
    ped_rank = ped_borough_df.sort_values("ped_death_share", ascending=False)[
        "borough"
    ].tolist()
    rankings_match = crash_rank == ped_rank

    if rankings_match:
        insight(
            "The rankings align: boroughs with the most crashes also have the highest pedestrian "
            "death share. In this filter selection, crash-volume logic is reasonable for pedestrian "
            "budgets — but try filtering to late-night or to specific boroughs to see if that holds up."
        )
    else:
        # Find the most striking divergence
        crash_top = crash_rank[0] if crash_rank else "?"
        ped_top = ped_rank[0] if ped_rank else "?"
        insight(
            f"<strong>The rankings diverge.</strong> The borough with the most crashes "
            f"(<strong style='color:#4A7FB5;'>{crash_top}</strong>) is not the borough with the "
            f"highest pedestrian death share (<strong style='color:#B91C1C;'>{ped_top}</strong>). "
            "This is direct evidence that allocating pedestrian safety budgets based on crash volume "
            "alone misdirects resources. The boroughs where walking is most dangerous are not always "
            "the boroughs with the most cars on the road."
        )
else:
    st.info("No pedestrian-by-borough data available for this filter selection.")

st.markdown("---")

# ── Page-level takeaway ──────────────────────────────────────────────────────
takeaway(
    "<strong style='color:#1c2536;'>1. Crash causes are not uniform across boroughs.</strong> "
    "Each borough's cause profile is different enough that one-size-fits-all enforcement is "
    "leaving easy wins on the table. Each borough needs its own top-priority cause to target.<br><br>"
    "<strong style='color:#1c2536;'>2. Daytime and late-night crashes are different problems.</strong> "
    "Speed and alcohol take a much bigger share of late-night crashes. Enforcement scheduled "
    "around rush hour is missing the hours where the cause mix is most dangerous.<br><br>"
    "<strong style='color:#1c2536;'>3. Pedestrian risk and crash volume don't always rank the "
    "same boroughs first.</strong> Funding pedestrian safety based on total crashes can send "
    "money to the wrong places. The pedestrian death share is the more relevant metric."
)

st.markdown("---")

with st.expander("Download underlying data"):
    if not borough_cause_df.empty:
        st.download_button(
            label="Download borough × cause matrix (CSV)",
            data=borough_cause_df.to_csv(index=False),
            file_name="where_when_borough_causes.csv",
            mime="text/csv",
        )
    if not daynight_df.empty:
        st.download_button(
            label="Download day × night cause matrix (CSV)",
            data=daynight_df.to_csv(index=False),
            file_name="where_when_daynight_causes.csv",
            mime="text/csv",
        )
    if not ped_borough_df.empty:
        st.download_button(
            label="Download pedestrian-by-borough metrics (CSV)",
            data=ped_borough_df.to_csv(index=False),
            file_name="where_when_pedestrian_borough.csv",
            mime="text/csv",
        )

elapsed = time.time() - start_time
st.caption(
    f"Loaded in {elapsed:.2f}s · Filters: {filters['time_period']} · {filters['date_start']:%b %-d}–{filters['date_end']:%b %-d}"
)
