"""
Page 1 — The Big Picture.

Establishes the citywide baseline: total crashes, fatalities, and the high-level
patterns that look uniform on the surface. This page is intentionally broad —
it sets up the puzzle that pages 2–4 will unpack.
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
)

start_time = time.time()

# ── Sidebar filters ──────────────────────────────────────────────────────────
filters = render_filters()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-label">Module 1 · Citywide Baseline</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-family:JetBrains Mono,monospace;font-weight:600;font-size:2rem;"
    "color:#0F172A;margin-bottom:0.3rem;letter-spacing:-0.02em;'>The Big Picture</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.97rem;line-height:1.7;margin-bottom:1rem;'>"
    "Before drilling into specific patterns, we need to know the scale of the problem. "
    "This page shows citywide totals, daily trends, and the surface-level distribution "
    "across boroughs — the same averages a city-wide policy would be built on.</p>",
    unsafe_allow_html=True,
)

render_context_bar("Citywide totals & trends", filters)

# ── Build SQL fragments from filters ─────────────────────────────────────────
borough_filter_sql = (
    "AND UPPER(borough) IN UNNEST(@boroughs)"
    if len(filters["boroughs"]) < 5
    else ""
)


# ── Cached query functions ───────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_kpis(boroughs_tuple, date_start, date_end, time_period):
    time_clause = time_period_sql_clause(time_period, "EXTRACT(HOUR FROM crash_date)")
    bf = "AND UPPER(borough) IN UNNEST(@boroughs)" if len(boroughs_tuple) < 5 else ""
    query = f"""
    SELECT
        COUNT(*)                                                AS total_crashes,
        SUM(number_of_persons_injured)                          AS total_injured,
        SUM(number_of_persons_killed)                           AS total_killed,
        SUM(number_of_pedestrians_killed)                       AS pedestrians_killed,
        SUM(number_of_cyclist_killed)                           AS cyclists_killed
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
      AND DATE(crash_date) BETWEEN @date_start AND @date_end
      {bf}
      {time_clause}
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ArrayQueryParameter("boroughs", "STRING", [b.upper() for b in boroughs_tuple]),
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end",   "DATE", date_end),
        ]
    )
    return get_bigquery_client().query(query, job_config=job_config).to_dataframe(create_bqstorage_client=False).iloc[0]


@st.cache_data(ttl=3600, show_spinner=False)
def load_daily_trend(boroughs_tuple, date_start, date_end, time_period):
    time_clause = time_period_sql_clause(time_period, "EXTRACT(HOUR FROM crash_date)")
    bf = "AND UPPER(borough) IN UNNEST(@boroughs)" if len(boroughs_tuple) < 5 else ""
    query = f"""
    SELECT
        DATE(crash_date) AS date,
        COUNT(*)         AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
      AND DATE(crash_date) BETWEEN @date_start AND @date_end
      {bf}
      {time_clause}
    GROUP BY date
    ORDER BY date
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ArrayQueryParameter("boroughs", "STRING", [b.upper() for b in boroughs_tuple]),
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end",   "DATE", date_end),
        ]
    )
    return get_bigquery_client().query(query, job_config=job_config).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600, show_spinner=False)
def load_borough_split(date_start, date_end, time_period):
    time_clause = time_period_sql_clause(time_period, "EXTRACT(HOUR FROM crash_date)")
    query = f"""
    SELECT
        INITCAP(borough) AS borough,
        COUNT(*)         AS crashes,
        SUM(number_of_persons_killed) AS killed
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
      AND DATE(crash_date) BETWEEN @date_start AND @date_end
      AND borough IS NOT NULL AND TRIM(borough) != ''
      {time_clause}
    GROUP BY borough
    ORDER BY crashes DESC
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end",   "DATE", date_end),
        ]
    )
    return get_bigquery_client().query(query, job_config=job_config).to_dataframe(create_bqstorage_client=False)


# ── Parallel loading ─────────────────────────────────────────────────────────
boroughs_tuple = tuple(sorted(filters["boroughs"]))

with st.spinner("Loading data from BigQuery..."):
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_kpi = pool.submit(load_kpis, boroughs_tuple, filters["date_start"], filters["date_end"], filters["time_period"])
        f_daily = pool.submit(load_daily_trend, boroughs_tuple, filters["date_start"], filters["date_end"], filters["time_period"])
        f_borough = pool.submit(load_borough_split, filters["date_start"], filters["date_end"], filters["time_period"])

    kpi = f_kpi.result()
    daily_df = f_daily.result()
    borough_df = f_borough.result()

if daily_df.empty:
    st.warning("No data matches the current filters. Try widening your selection.")
    st.stop()

# ── KPI row ──────────────────────────────────────────────────────────────────
total_crashes = int(kpi["total_crashes"] or 0)
total_injured = int(kpi["total_injured"] or 0)
total_killed = int(kpi["total_killed"] or 0)
fatality_rate = (total_killed / total_crashes * 100) if total_crashes else 0
ped_killed = int(kpi["pedestrians_killed"] or 0)
cyc_killed = int(kpi["cyclists_killed"] or 0)

st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "At a Glance</h3>",
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Crashes", f"{total_crashes:,}")
c2.metric("People Injured", f"{total_injured:,}")
c3.metric("Fatalities", f"{total_killed:,}")
c4.metric("Pedestrian Deaths", f"{ped_killed:,}")
c5.metric("Cyclist Deaths", f"{cyc_killed:,}")

# ── Formulas backing the KPIs ────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;"
    "font-size:0.95rem;'>How the headline metrics are calculated</h4>",
    unsafe_allow_html=True,
)

formula_box(
    "Formula 1 — Crash Fatality Rate",
    f"Fatality Rate = ( Total Killed ÷ Total Crashes ) × 100<br>"
    f"= ( {total_killed:,} ÷ {total_crashes:,} ) × 100 = <strong style='color:#4A7FB5;'>{fatality_rate:.2f}%</strong>",
    "The share of crashes that result in at least one death. This is the headline severity metric — "
    "the lower the better.",
)

formula_box(
    "Formula 2 — Vulnerable Road User Death Share",
    f"VRU Death Share = ( Pedestrian + Cyclist Deaths ) ÷ Total Deaths × 100<br>"
    f"= ( {ped_killed:,} + {cyc_killed:,} ) ÷ {total_killed:,} × 100 = "
    f"<strong style='color:#4A7FB5;'>"
    f"{(ped_killed + cyc_killed) / total_killed * 100 if total_killed else 0:.1f}%</strong>",
    "The share of NYC traffic deaths that are pedestrians or cyclists. A high share means "
    "the people without vehicles around them are bearing most of the cost.",
)

st.markdown("---")

# ── Daily trend ──────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Daily crash volume — what does the citywide trend look like?</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "The grey line shows raw daily counts; the blue line is the 7-day rolling average. "
    "We're looking for sustained changes, not single-day spikes.</p>",
    unsafe_allow_html=True,
)

daily_df["date"] = pd.to_datetime(daily_df["date"])
daily_df = daily_df.sort_values("date")
daily_df["rolling_7"] = daily_df["crashes"].rolling(7, min_periods=1).mean().round(1)

formula_box(
    "Formula 3 — 7-Day Rolling Average",
    "Rolling Avg(t) = ( Crashes(t-6) + Crashes(t-5) + ... + Crashes(t) ) ÷ 7",
    "Smooths out day-to-day noise (weekend dips, weather spikes) so that real trends become visible.",
)

raw_line = (
    alt.Chart(daily_df)
    .mark_line(opacity=0.3, strokeWidth=1, color="#94A3B8")
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("crashes:Q", title="Crashes"),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("crashes:Q", title="Crashes"),
        ],
    )
)
rolling_line = (
    alt.Chart(daily_df)
    .mark_line(strokeWidth=2.5, color=SIPA_BLUE)
    .encode(
        x="date:T",
        y="rolling_7:Q",
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("rolling_7:Q", title="7-day avg", format=".1f"),
        ],
    )
)
st.altair_chart(
    (raw_line + rolling_line).properties(height=300), use_container_width=True
)

insight(
    "Crash volume oscillates day-to-day but the 7-day rolling average reveals whether a sustained "
    "increase or decrease is underway. Single-day spikes are usually weather, holidays, or reporting "
    "anomalies — only the rolling average tells us about the underlying trend the city is on."
)

st.markdown("---")

# ── Borough split ────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "How are crashes distributed across boroughs?</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "This is the surface-level picture: which boroughs see the most crashes overall? "
    "Pages 2–4 will show why this ranking is misleading on its own.</p>",
    unsafe_allow_html=True,
)

# Two side-by-side: total crashes & total deaths
borough_df["share"] = borough_df["crashes"] / borough_df["crashes"].sum() * 100

formula_box(
    "Formula 4 — Borough Share of Total Crashes",
    "Borough Share = ( Crashes in Borough ÷ Citywide Crashes ) × 100",
    "How much of the city's total crash burden falls in each borough. Bigger boroughs naturally "
    "have higher shares — but the gap between them tells us how concentrated the problem is.",
)

col_l, col_r = st.columns(2)

with col_l:
    crash_chart = (
        alt.Chart(borough_df)
        .mark_bar(cornerRadiusEnd=4, color=SIPA_BLUE)
        .encode(
            x=alt.X("crashes:Q", title="Total crashes"),
            y=alt.Y("borough:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("borough:N", title="Borough"),
                alt.Tooltip("crashes:Q", title="Crashes", format=","),
                alt.Tooltip("share:Q", title="Share", format=".1f"),
            ],
        )
        .properties(height=200, title="Total crashes by borough")
    )
    st.altair_chart(crash_chart, use_container_width=True)

with col_r:
    death_chart = (
        alt.Chart(borough_df)
        .mark_bar(cornerRadiusEnd=4, color=ACCENT_AMBER)
        .encode(
            x=alt.X("killed:Q", title="Total deaths"),
            y=alt.Y("borough:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("borough:N", title="Borough"),
                alt.Tooltip("killed:Q", title="Deaths", format=","),
            ],
        )
        .properties(height=200, title="Total deaths by borough")
    )
    st.altair_chart(death_chart, use_container_width=True)

insight(
    "On the surface, Brooklyn and Queens dominate both crash volume and total deaths — and a "
    "city-wide policy built on this single ranking would direct most resources there. But this "
    "view says nothing about <em>per-crash severity</em>, <em>which causes are dominant where</em>, "
    "or <em>which boroughs are most dangerous for pedestrians specifically</em>. That's what the "
    "next three modules unpack."
)

st.markdown("---")

# ── Page-level takeaway ──────────────────────────────────────────────────────
takeaway(
    "<strong style='color:#1c2536;'>1. The headline numbers are real, but they hide as much as they reveal.</strong> "
    "Brooklyn and Queens lead in raw crashes and deaths — that part is true. But a policy built on "
    "raw counts alone treats every crash as equivalent.<br><br>"
    "<strong style='color:#1c2536;'>2. The next three modules unpack what the averages are hiding.</strong> "
    "Module 2 shows that pedestrians and cyclists bear a disproportionate share of deaths. "
    "Module 3 shows that crash <em>causes</em> vary by borough and by time of day. "
    "Module 4 translates these findings into specific policy levers.<br><br>"
    "<strong style='color:#1c2536;'>3. Use the sidebar filters to test sensitivity.</strong> "
    "Filter to late-night hours, or to a single borough, and watch how the picture changes — "
    "that's the precision policy argument in action."
)

st.markdown("---")

# ── Download ─────────────────────────────────────────────────────────────────
with st.expander("Download underlying data"):
    st.download_button(
        label="Download daily crash trend (CSV)",
        data=daily_df.to_csv(index=False),
        file_name="big_picture_daily_trend.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download borough-level summary (CSV)",
        data=borough_df.to_csv(index=False),
        file_name="big_picture_borough_summary.csv",
        mime="text/csv",
    )

elapsed = time.time() - start_time
st.caption(f"Loaded in {elapsed:.2f}s · Filters: {len(filters['boroughs'])} boroughs · {filters['time_period']}")