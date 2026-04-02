import time
from concurrent.futures import ThreadPoolExecutor
import altair as alt
import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

start_time = time.time()

PROJECT_ID = "sipa-adv-c-sparkly-pickle"


# ── Altair theme ──────────────────────────────────────────────────────────────
@alt.theme.register("app_dark", enable=True)
def app_dark():
    return {
        "config": {
            "background": "#1a1c27",
            "view": {"stroke": "transparent"},
            "axis": {
                "gridColor": "#2a2a3a",
                "domainColor": "#2a2a3a",
                "tickColor": "#2a2a3a",
                "labelColor": "#6a6258",
                "titleColor": "#9b9488",
                "labelFont": "Inter, sans-serif",
                "titleFont": "Inter, sans-serif",
                "labelFontSize": 11,
                "titleFontSize": 12,
            },
            "legend": {
                "labelColor": "#9b9488",
                "titleColor": "#c9c4bc",
                "labelFont": "Inter, sans-serif",
                "titleFont": "Inter, sans-serif",
                "labelFontSize": 11,
            },
            "title": {
                "color": "#e8e0d4",
                "font": "Inter, sans-serif",
                "fontSize": 14,
                "fontWeight": 500,
            },
        }
    }


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-label">Page 3 · Merged Dataset · 2026 Live</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-family:Lora,serif;font-weight:500;font-size:2.2rem;"
    "color:#b45309;margin-bottom:0.3rem;'>Motor Vehicle Collisions – Merged Dataset (2026 Live)</h1>",
    unsafe_allow_html=True,
)
st.write(
    """
    This page merges two live 2026 NYC collision datasets to support broader exploratory analysis.
    By combining person-level and crash-level data, we can examine trends across time and location.
    """
)


# ── BigQuery client ───────────────────────────────────────────────────────────
@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


# ── Individual cached query functions ────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_daily_counts():
    query = """
    SELECT date, crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.daily_crash_counts_2026`
    ORDER BY date
    """
    return (
        get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600)
def load_borough_counts():
    query = """
    SELECT borough, crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.borough_crash_counts_2026`
    WHERE borough IS NOT NULL AND TRIM(borough) != ''
    ORDER BY crashes DESC
    """
    return (
        get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600)
def load_contributing_factors():
    query = """
    SELECT
        contributing_factor_vehicle_1 AS factor,
        COUNT(*) AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE contributing_factor_vehicle_1 IS NOT NULL
      AND LOWER(contributing_factor_vehicle_1) NOT IN ('unspecified', '')
      AND EXTRACT(YEAR FROM crash_date) = 2026
    GROUP BY factor
    ORDER BY crashes DESC
    LIMIT 10
    """
    return (
        get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600)
def load_victim_trends():
    query = """
    SELECT
        DATE_TRUNC(crash_date, MONTH)          AS month,
        SUM(number_of_pedestrians_killed)      AS pedestrians_killed,
        SUM(number_of_cyclist_killed)          AS cyclists_killed,
        SUM(number_of_motorist_killed)         AS motorists_killed
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
    GROUP BY month
    ORDER BY month
    """
    return (
        get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    )


# ── Parallel loading ──────────────────────────────────────────────────────────
with st.spinner("Loading data from BigQuery..."):
    with ThreadPoolExecutor(max_workers=4) as pool:
        f_daily = pool.submit(load_daily_counts)
        f_borough = pool.submit(load_borough_counts)
        f_factors = pool.submit(load_contributing_factors)
        f_victim = pool.submit(load_victim_trends)

    daily_counts = f_daily.result()
    borough_counts = f_borough.result()
    factors_df = f_factors.result()
    victim_df = f_victim.result()

if daily_counts.empty:
    st.warning("No data available.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
daily_counts["date"] = pd.to_datetime(daily_counts["date"])
daily_counts = daily_counts.sort_values("date")
daily_counts["rolling_7"] = (
    daily_counts["crashes"].rolling(7, min_periods=1).mean().round(1)
)

total = int(daily_counts["crashes"].sum())
peak = int(daily_counts["crashes"].max())
avg = daily_counts["crashes"].mean()
top_b = borough_counts.iloc[0]["borough"].title() if not borough_counts.empty else "N/A"

st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>At a glance</h3>",
    unsafe_allow_html=True,
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Crashes (YTD)", f"{total:,}")
c2.metric("Avg Crashes / Day", f"{avg:.1f}")
c3.metric("Peak Single Day", f"{peak:,}")
c4.metric("Highest-Risk Borough", top_b)

st.markdown("---")

# ── Chart 1: Daily trend + rolling avg ───────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>Daily Trend Analysis</h3>",
    unsafe_allow_html=True,
)
st.write(
    """
    This chart shows how crash counts change over time.
    It helps identify fluctuations and short-term patterns in collision activity.
    The orange line shows the 7-day rolling average to smooth out noise.
    """
)

raw_line = (
    alt.Chart(daily_counts)
    .mark_line(opacity=0.25, strokeWidth=1, color="#6a6258")
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
    alt.Chart(daily_counts)
    .mark_line(strokeWidth=2.5, color="#b45309")
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

st.markdown(
    """
    <div class="insight-box">
        <strong style="color:#b45309;">Key Insight</strong><br>
        Crash counts fluctuate across time rather than remaining constant.
        Most days fall within a moderate range, suggesting a relatively stable baseline level of collisions.
        Occasional spikes indicate days with unusually high activity, which may be influenced by traffic patterns,
        weather conditions, or other external factors.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Chart 2: Borough bar ──────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>Borough Analysis</h3>",
    unsafe_allow_html=True,
)
st.write(
    """
    This chart compares crash counts across boroughs,
    highlighting geographic differences in collision patterns.
    Click a bar to highlight it.
    """
)

borough_counts["borough"] = borough_counts["borough"].str.title()
borough_sel = alt.selection_point(fields=["borough"])

borough_chart = (
    alt.Chart(borough_counts)
    .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3)
    .encode(
        x=alt.X("crashes:Q", title="Number of crashes"),
        y=alt.Y("borough:N", sort="-x", title=None),
        color=alt.condition(borough_sel, alt.value("#b45309"), alt.value("#2a2a3a")),
        tooltip=[
            alt.Tooltip("borough:N", title="Borough"),
            alt.Tooltip("crashes:Q", title="Crashes", format=","),
        ],
    )
    .add_params(borough_sel)
    .properties(height=220)
)

st.altair_chart(borough_chart, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
        <strong style="color:#b45309;">Key Insight</strong><br>
        The borough-level comparison reveals that motor vehicle collisions are unevenly distributed
        across New York City. These differences are likely driven by variations in population density,
        traffic volume, and urban infrastructure — highlighting the importance of geographically
        differentiated policy responses rather than one-size-fits-all solutions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Chart 3: Contributing factors ────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>Top 10 Contributing Factors</h3>",
    unsafe_allow_html=True,
)
st.write(
    """
    What causes most crashes? Based on the primary contributing factor recorded by police at the scene.
    This helps identify whether interventions should target behavioral change, infrastructure, or enforcement.
    """
)

factors_chart = (
    alt.Chart(factors_df)
    .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3, color="#b45309")
    .encode(
        x=alt.X("crashes:Q", title="Number of crashes"),
        y=alt.Y("factor:N", sort="-x", title=None),
        tooltip=[
            alt.Tooltip("factor:N", title="Factor"),
            alt.Tooltip("crashes:Q", title="Crashes", format=","),
        ],
    )
    .properties(height=320)
)

st.altair_chart(factors_chart, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
        <strong style="color:#b45309;">Key Insight</strong><br>
        Driver inattention and distraction typically leads by a wide margin, followed by
        failure to yield and following too closely. These behavioral factors suggest that
        enforcement and awareness campaigns may be more effective than infrastructure
        changes alone for reducing crash frequency.
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Chart 4: Monthly fatalities ───────────────────────────────────────────────
if not victim_df.empty and victim_df["month"].notna().any():
    st.markdown("---")
    st.markdown(
        "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>"
        "Monthly Fatalities by Victim Type</h3>",
        unsafe_allow_html=True,
    )
    st.write(
        """
        Tracking pedestrian, cyclist, and motorist fatalities month by month.
        This directly addresses Research Question 3 — temporal patterns — and helps assess
        whether Vision Zero initiatives are reducing risk over time.
        """
    )

    victim_df["month"] = pd.to_datetime(victim_df["month"])
    victim_long = victim_df.melt(
        id_vars="month",
        value_vars=["pedestrians_killed", "cyclists_killed", "motorists_killed"],
        var_name="victim_type",
        value_name="killed",
    )
    victim_long["victim_type"] = victim_long["victim_type"].map(
        {
            "pedestrians_killed": "Pedestrian",
            "cyclists_killed": "Cyclist",
            "motorists_killed": "Motorist",
        }
    )

    victim_color = alt.Scale(
        domain=["Pedestrian", "Cyclist", "Motorist"],
        range=["#b45309", "#d97706", "#4a7fb5"],
    )

    victim_chart = (
        alt.Chart(victim_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:T", title="Month"),
            y=alt.Y("killed:Q", title="Fatalities"),
            color=alt.Color(
                "victim_type:N",
                scale=victim_color,
                legend=alt.Legend(title="Victim type", orient="top"),
            ),
            tooltip=[
                alt.Tooltip("month:T", title="Month"),
                alt.Tooltip("victim_type:N", title="Type"),
                alt.Tooltip("killed:Q", title="Killed"),
            ],
        )
        .properties(height=280)
    )

    st.altair_chart(victim_chart, use_container_width=True)

    st.markdown(
        """
        <div class="insight-box">
            <strong style="color:#b45309;">Key Insight</strong><br>
            Pedestrians consistently account for the largest share of fatalities.
            Monitoring these trends monthly helps assess whether Vision Zero
            initiatives are reducing risk for the most vulnerable road users over time.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Download ──────────────────────────────────────────────────────────────────
with st.expander("Download underlying data"):
    st.download_button(
        label="Download daily counts (CSV)",
        data=daily_counts.to_csv(index=False),
        file_name="daily_crash_counts_2026.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download borough counts (CSV)",
        data=borough_counts.to_csv(index=False),
        file_name="borough_crash_counts_2026.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download contributing factors (CSV)",
        data=factors_df.to_csv(index=False),
        file_name="contributing_factors_2026.csv",
        mime="text/csv",
    )

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
