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
    '<span class="page-label">Page 2 · Person-Level Dataset</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-family:Lora,serif;font-weight:500;font-size:2.2rem;"
    "color:#b45309;margin-bottom:0.3rem;'>Motor Vehicle Collisions – Person (BigQuery)</h1>",
    unsafe_allow_html=True,
)
st.write(
    """
    This page uses the person-level motor vehicle collisions dataset stored in BigQuery.
    It explores temporal patterns, who gets hurt, and the role of safety equipment.
    """
)


# ── BigQuery client ───────────────────────────────────────────────────────────
@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


# ── Individual query functions (each cached independently) ────────────────────
@st.cache_data(ttl=3600)
def load_kpi_metrics():
    query = """
    SELECT
        COUNT(DISTINCT collision_id)                                      AS total_crashes,
        COUNTIF(LOWER(person_injury) = 'injured')                        AS total_injured,
        COUNTIF(LOWER(person_injury) = 'killed')                         AS total_killed,
        ROUND(
            COUNTIF(LOWER(person_injury) = 'killed') * 100.0
            / NULLIF(COUNT(*), 0), 2
        )                                                                 AS fatality_rate
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE crash_date IS NOT NULL
    """
    return (
        get_bigquery_client()
        .query(query)
        .to_dataframe(create_bqstorage_client=False)
        .iloc[0]
    )


@st.cache_data(ttl=3600)
def load_weekday_person_type():
    query = """
    SELECT
        FORMAT_DATE('%A', DATE(crash_date)) AS weekday,
        CASE
            WHEN LOWER(person_type) LIKE '%pedestrian%' THEN 'Pedestrian'
            WHEN LOWER(person_type) LIKE '%bicyclist%'  THEN 'Cyclist'
            WHEN LOWER(person_type) LIKE '%driver%'     THEN 'Driver'
            WHEN LOWER(person_type) LIKE '%occupant%'   THEN 'Occupant'
            ELSE 'Other'
        END AS person_type,
        COUNT(*) AS people
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE crash_date IS NOT NULL
      AND person_type IS NOT NULL
    GROUP BY weekday, person_type
    """
    df = get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df["weekday"] = pd.Categorical(df["weekday"], categories=order, ordered=True)
    return df.sort_values("weekday")


@st.cache_data(ttl=3600)
def load_hour_weekday_heatmap():
    query = """
    SELECT
        FORMAT_DATE('%A', DATE(crash_date)) AS weekday,
        EXTRACT(HOUR FROM crash_date)       AS hour,
        COUNT(DISTINCT collision_id)        AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE crash_date IS NOT NULL
    GROUP BY weekday, hour
    """
    df = get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df["weekday"] = pd.Categorical(df["weekday"], categories=order, ordered=True)
    return df


@st.cache_data(ttl=3600)
def load_safety_equipment():
    query = """
    SELECT
        CASE
            WHEN safety_equipment IS NULL OR TRIM(safety_equipment) = ''
                THEN 'Unknown / Not recorded'
            WHEN LOWER(safety_equipment) LIKE '%lap belt%'
              OR LOWER(safety_equipment) LIKE '%shoulder%'
              OR LOWER(safety_equipment) LIKE '%harness%'
                THEN 'Seatbelt worn'
            WHEN LOWER(safety_equipment) LIKE '%none%'
                THEN 'No safety equipment'
            WHEN LOWER(safety_equipment) LIKE '%helmet%'
                THEN 'Helmet worn'
            WHEN LOWER(safety_equipment) LIKE '%air bag%'
              OR LOWER(safety_equipment) LIKE '%airbag%'
                THEN 'Airbag deployed'
            ELSE 'Other equipment'
        END AS equipment,
        CASE
            WHEN LOWER(person_injury) = 'killed'  THEN 'Killed'
            WHEN LOWER(person_injury) = 'injured' THEN 'Injured'
            ELSE 'No injury'
        END AS outcome,
        COUNT(*) AS people
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE person_type IN ('Driver', 'Occupant')
      AND person_injury IS NOT NULL
    GROUP BY equipment, outcome
    """
    return (
        get_bigquery_client().query(query).to_dataframe(create_bqstorage_client=False)
    )


# ── Parallel loading ──────────────────────────────────────────────────────────
with st.spinner("Loading data from BigQuery..."):
    with ThreadPoolExecutor(max_workers=4) as pool:
        f_kpi = pool.submit(load_kpi_metrics)
        f_weekday = pool.submit(load_weekday_person_type)
        f_heatmap = pool.submit(load_hour_weekday_heatmap)
        f_safety = pool.submit(load_safety_equipment)

    kpi = f_kpi.result()
    weekday_df = f_weekday.result()
    heatmap_df = f_heatmap.result()
    safety_df = f_safety.result()

if weekday_df.empty:
    st.warning("No data available.")
    st.stop()

# ── KPI metrics ───────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>At a glance</h3>",
    unsafe_allow_html=True,
)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total crashes", f"{int(kpi['total_crashes']):,}")
col2.metric("People injured", f"{int(kpi['total_injured']):,}")
col3.metric("Fatalities", f"{int(kpi['total_killed']):,}")
col4.metric("Fatality rate", f"{kpi['fatality_rate']:.2f}%")

st.markdown("---")

# ── Chart 1: Stacked bar ──────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>Who gets hurt, and when?</h3>",
    unsafe_allow_html=True,
)
st.write(
    """
    Each bar shows the total number of people involved in crashes on that day,
    broken down by their role - driver, occupant, pedestrian, or cyclist.
    This reveals not just when crashes peak, but who bears the risk.
    """
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

type_color_scale = alt.Scale(
    domain=["Driver", "Occupant", "Pedestrian", "Cyclist", "Other"],
    range=["#185FA5", "#85B7EB", "#b45309", "#1D9E75", "#888780"],
)

selection = alt.selection_point(fields=["person_type"], bind="legend")

stacked_bar = (
    alt.Chart(weekday_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "weekday:N",
            sort=weekday_order,
            title="Day of week",
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y("people:Q", title="Number of people"),
        color=alt.Color(
            "person_type:N",
            scale=type_color_scale,
            legend=alt.Legend(title="Person type", orient="top"),
        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=[
            alt.Tooltip("weekday:N", title="Day"),
            alt.Tooltip("person_type:N", title="Person type"),
            alt.Tooltip("people:Q", title="Count", format=","),
        ],
    )
    .add_params(selection)
    .properties(height=320)
)

st.altair_chart(stacked_bar, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
        <strong style="color:#b45309;">Key Insight</strong><br>
        Fridays consistently show the highest overall count, driven mainly by driver and occupant
        involvement. Pedestrian risk remains relatively stable across the week but spikes slightly
        on weekends, likely reflecting night-time activity patterns.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Chart 2: Heatmap ──────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>When do crashes happen? Hour × day heatmap</h3>",
    unsafe_allow_html=True,
)
st.write(
    """
    Each cell encodes crash count for that hour-day combination.
    Darker cells mean more crashes. This reveals commuter peaks, late-night patterns,
    and how weekends differ from weekdays.
    """
)

heatmap_df["hour_label"] = heatmap_df["hour"].apply(
    lambda h: (
        "12a"
        if h == 0
        else ("12p" if h == 12 else (f"{h}a" if h < 12 else f"{h - 12}p"))
    )
)

hour_label_order = [
    "12a",
    "1a",
    "2a",
    "3a",
    "4a",
    "5a",
    "6a",
    "7a",
    "8a",
    "9a",
    "10a",
    "11a",
    "12p",
    "1p",
    "2p",
    "3p",
    "4p",
    "5p",
    "6p",
    "7p",
    "8p",
    "9p",
    "10p",
    "11p",
]

heatmap = (
    alt.Chart(heatmap_df)
    .mark_rect()
    .encode(
        x=alt.X(
            "hour_label:O",
            sort=hour_label_order,
            title="Hour of day",
            axis=alt.Axis(labelAngle=0, labelFontSize=10),
        ),
        y=alt.Y("weekday:O", sort=weekday_order, title=None),
        color=alt.Color(
            "crashes:Q",
            scale=alt.Scale(scheme="oranges"),
            legend=alt.Legend(title="Crashes"),
        ),
        tooltip=[
            alt.Tooltip("weekday:N", title="Day"),
            alt.Tooltip("hour_label:O", title="Hour"),
            alt.Tooltip("crashes:Q", title="Crashes", format=","),
        ],
    )
    .add_params(alt.selection_interval(encodings=["x"]))
    .properties(height=220)
)

st.altair_chart(heatmap, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
        <strong style="color:#b45309;">Key Insight</strong><br>
        The classic double-peak commuter pattern appears strongly on weekdays —
        8–9 am and 4–6 pm. Weekend nights (Friday and Saturday after 10 pm) show a
        distinct elevated risk band absent on weekdays, consistent with recreational travel.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Chart 3: Safety equipment ─────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:Lora,serif;font-weight:500;color:#b45309;'>Does safety equipment make a difference?</h3>",
    unsafe_allow_html=True,
)
st.write(
    """
    Among drivers and occupants, this chart compares injury outcomes across
    different safety equipment states, offering a direct look at the protective
    effect of seatbelts and airbags.
    """
)

safety_filtered = safety_df[
    safety_df["equipment"].isin(
        ["Seatbelt worn", "No safety equipment", "Airbag deployed", "Other equipment"]
    )
    & safety_df["outcome"].isin(["Killed", "Injured", "No injury"])
].copy()

outcome_color_scale = alt.Scale(
    domain=["No injury", "Injured", "Killed"],
    range=["#1D9E75", "#EF9F27", "#E24B4A"],
)

safety_chart = (
    alt.Chart(safety_filtered)
    .mark_bar()
    .encode(
        x=alt.X(
            "people:Q",
            title="Number of people",
            stack="normalize",
            axis=alt.Axis(format="%"),
        ),
        y=alt.Y("equipment:N", title=None, sort="-x"),
        color=alt.Color(
            "outcome:N",
            scale=outcome_color_scale,
            legend=alt.Legend(title="Outcome", orient="top"),
        ),
        tooltip=[
            alt.Tooltip("equipment:N", title="Equipment"),
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("people:Q", title="Count", format=","),
        ],
    )
    .properties(height=200)
)

st.altair_chart(safety_chart, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
        <strong style="color:#b45309;">Key Insight</strong><br>
        People with no safety equipment show a notably higher proportion of serious injuries
        and fatalities compared to those wearing seatbelts. The 'Unknown / Not recorded'
        category is large — a known limitation of police-reported data — so interpret
        absolute proportions with caution.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Download ──────────────────────────────────────────────────────────────────
with st.expander("Download underlying data"):
    st.download_button(
        label="Download weekday x person type (CSV)",
        data=weekday_df.to_csv(index=False),
        file_name="weekday_person_type.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download hour x weekday heatmap (CSV)",
        data=heatmap_df.to_csv(index=False),
        file_name="hour_weekday_heatmap.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download safety equipment outcomes (CSV)",
        data=safety_df.to_csv(index=False),
        file_name="safety_equipment_outcomes.csv",
        mime="text/csv",
    )

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
