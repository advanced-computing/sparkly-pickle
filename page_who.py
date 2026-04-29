"""
Page 2 — Who Bears the Risk.

Person-level analysis: who is actually getting hurt and dying in NYC traffic?
Pedestrians and cyclists are a small share of crash involvement but a large
share of deaths. This page proves that with rates, not raw counts.
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
    insight,
    takeaway,
    SIPA_BLUE,
    ACCENT_AMBER,
    ACCENT_GREEN,
    ACCENT_RED,
)

start_time = time.time()

# ── Sidebar filters ──────────────────────────────────────────────────────────
filters = render_filters()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-label">Module 2 · Vulnerability Analysis</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-family:JetBrains Mono,monospace;font-weight:600;font-size:2rem;"
    "color:#0F172A;margin-bottom:0.3rem;letter-spacing:-0.02em;'>Who Bears the Risk</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.97rem;line-height:1.7;margin-bottom:1rem;'>"
    "Module 1 showed total crash counts. Now we ask the next question: <em>per crash involvement</em>, "
    "who is most likely to die? If pedestrians and cyclists are a small share of people involved but "
    "a large share of deaths, that's evidence the city's most vulnerable road users need targeted "
    "protection — not just driver-focused enforcement.</p>",
    unsafe_allow_html=True,
)

render_context_bar("Person-level outcomes by road user type", filters)

# ── Cached queries ───────────────────────────────────────────────────────────
person_filter_sql = (
    ""
    if len(filters["person_types"]) == 4
    else "AND person_type_clean IN UNNEST(@person_types)"
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_person_outcomes(person_types_key, date_start, date_end, time_period):
    # Person table's crash_date is date-only — to filter by hour we must join
    # with the Crash table which has a full timestamp.
    if time_period == "Daytime (6am–10pm)":
        time_join_clause = """
        JOIN (
            SELECT collision_id
            FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
            WHERE EXTRACT(HOUR FROM crash_date) BETWEEN 6 AND 21
        ) c USING (collision_id)
        """
    elif time_period == "Late night (10pm–6am)":
        time_join_clause = """
        JOIN (
            SELECT collision_id
            FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
            WHERE EXTRACT(HOUR FROM crash_date) >= 22 OR EXTRACT(HOUR FROM crash_date) < 6
        ) c USING (collision_id)
        """
    else:
        time_join_clause = ""

    pf = (
        "AND person_type_clean IN UNNEST(@person_types)"
        if person_types_key != "all"
        else ""
    )
    query = f"""
    WITH classified AS (
        SELECT
            CASE
                WHEN LOWER(p.person_type) LIKE '%pedestrian%' THEN 'Pedestrian'
                WHEN LOWER(p.person_type) LIKE '%bicyclist%'  THEN 'Cyclist'
                WHEN LOWER(p.person_type) LIKE '%driver%'     THEN 'Driver'
                WHEN LOWER(p.person_type) LIKE '%occupant%'   THEN 'Occupant'
                ELSE 'Other'
            END AS person_type_clean,
            CASE
                WHEN LOWER(p.person_injury) = 'killed'  THEN 'Killed'
                WHEN LOWER(p.person_injury) = 'injured' THEN 'Injured'
                ELSE 'No injury'
            END AS outcome
        FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person` p
        {time_join_clause}
        WHERE p.crash_date IS NOT NULL
          AND DATE(p.crash_date) BETWEEN @date_start AND @date_end
          AND p.person_type IS NOT NULL
    )
    SELECT person_type_clean, outcome, COUNT(*) AS people
    FROM classified
    WHERE person_type_clean != 'Other'
      {pf}
    GROUP BY person_type_clean, outcome
    """
    job_config = bq.QueryJobConfig(
        query_parameters=[
            bq.ScalarQueryParameter("date_start", "DATE", date_start),
            bq.ScalarQueryParameter("date_end", "DATE", date_end),
            bq.ArrayQueryParameter("person_types", "STRING", filters["person_types"]),
        ]
    )
    return (
        get_bigquery_client()
        .query(query, job_config=job_config)
        .to_dataframe(create_bqstorage_client=False)
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_safety_equipment(date_start, date_end, time_period):
    # Same fix as load_person_outcomes — Person table has date-only,
    # so we join to Crash table for hour-based filtering.
    if time_period == "Daytime (6am–10pm)":
        time_join_clause = """
        JOIN (
            SELECT collision_id
            FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
            WHERE EXTRACT(HOUR FROM crash_date) BETWEEN 6 AND 21
        ) c USING (collision_id)
        """
    elif time_period == "Late night (10pm–6am)":
        time_join_clause = """
        JOIN (
            SELECT collision_id
            FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
            WHERE EXTRACT(HOUR FROM crash_date) >= 22 OR EXTRACT(HOUR FROM crash_date) < 6
        ) c USING (collision_id)
        """
    else:
        time_join_clause = ""

    query = f"""
    SELECT
        CASE
            WHEN p.safety_equipment IS NULL OR TRIM(p.safety_equipment) = ''
                THEN 'Unknown / Not recorded'
            WHEN LOWER(p.safety_equipment) LIKE '%lap belt%'
              OR LOWER(p.safety_equipment) LIKE '%shoulder%'
              OR LOWER(p.safety_equipment) LIKE '%harness%'
                THEN 'Seatbelt worn'
            WHEN LOWER(p.safety_equipment) LIKE '%none%'
                THEN 'No safety equipment'
            WHEN LOWER(p.safety_equipment) LIKE '%air bag%'
              OR LOWER(p.safety_equipment) LIKE '%airbag%'
                THEN 'Airbag deployed'
            ELSE 'Other equipment'
        END AS equipment,
        CASE
            WHEN LOWER(p.person_injury) = 'killed'  THEN 'Killed'
            WHEN LOWER(p.person_injury) = 'injured' THEN 'Injured'
            ELSE 'No injury'
        END AS outcome,
        COUNT(*) AS people
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person` p
    {time_join_clause}
    WHERE p.person_type IN ('Driver', 'Occupant')
      AND p.person_injury IS NOT NULL
      AND DATE(p.crash_date) BETWEEN @date_start AND @date_end
    GROUP BY equipment, outcome
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
person_types_key = (
    "all"
    if len(filters["person_types"]) == 4
    else "_".join(sorted(filters["person_types"]))
)

with st.spinner("Loading data from BigQuery..."):
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_person = pool.submit(
            load_person_outcomes,
            person_types_key,
            filters["date_start"],
            filters["date_end"],
            filters["time_period"],
        )
        f_safety = pool.submit(
            load_safety_equipment,
            filters["date_start"],
            filters["date_end"],
            filters["time_period"],
        )

    person_df = f_person.result()
    safety_df = f_safety.result()

if person_df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Compute fatality rates per person type ───────────────────────────────────
totals_by_type = person_df.groupby("person_type_clean")["people"].sum().rename("total")
killed_by_type = (
    person_df[person_df["outcome"] == "Killed"]
    .groupby("person_type_clean")["people"]
    .sum()
    .rename("killed")
)
rates = pd.concat([totals_by_type, killed_by_type], axis=1).fillna(0).reset_index()
rates["fatality_rate"] = (rates["killed"] / rates["total"] * 100).round(3)
rates = rates.sort_values("fatality_rate", ascending=False)

# ── KPI row — fatality rate per group ────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Fatality Rate by Road User Type</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "Of the people involved in a crash, what percent were killed? This is the headline severity "
    "metric — and it's the only fair way to compare risk across groups of very different sizes.</p>",
    unsafe_allow_html=True,
)

formula_box(
    "Formula 1 — Group Fatality Rate",
    "Fatality Rate (group) = ( Killed in group ÷ Total involved in group ) × 100",
    "Normalizing by total involvement is the key methodological step. Drivers outnumber pedestrians "
    "in the data ten-to-one, so comparing raw death counts would be misleading. Rates fix that.",
)

cols = st.columns(len(rates))
for col, (_, row) in zip(cols, rates.iterrows()):
    pt = row["person_type_clean"]
    rate = row["fatality_rate"]
    killed = int(row["killed"])
    total = int(row["total"])
    col.metric(
        label=f"{pt} fatality rate",
        value=f"{rate:.2f}%",
        delta=f"{killed:,} of {total:,}",
        delta_color="off",
    )

st.markdown("---")

# ── Stacked normalized bar — outcomes by person type ─────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Outcome composition by road user type</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "Each bar shows what percent of that group ended up killed, injured, or unhurt. "
    "Same y-axis scale across all groups means we're comparing risk per person, "
    "not group size.</p>",
    unsafe_allow_html=True,
)

outcome_color_scale = alt.Scale(
    domain=["No injury", "Injured", "Killed"],
    range=[ACCENT_GREEN, ACCENT_AMBER, ACCENT_RED],
)

stacked_chart = (
    alt.Chart(person_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "people:Q",
            title="Share of people in this group (%)",
            stack="normalize",
            axis=alt.Axis(format="%"),
        ),
        y=alt.Y(
            "person_type_clean:N",
            title=None,
            sort=["Pedestrian", "Cyclist", "Driver", "Occupant"],
        ),
        color=alt.Color(
            "outcome:N",
            scale=outcome_color_scale,
            legend=alt.Legend(title="Outcome", orient="top"),
        ),
        tooltip=[
            alt.Tooltip("person_type_clean:N", title="Group"),
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("people:Q", title="Count", format=","),
        ],
    )
    .properties(height=240)
)

st.altair_chart(stacked_chart, use_container_width=True)

# Compute the headline number for the insight: pedestrian fatality rate vs driver fatality rate
ped_row = rates[rates["person_type_clean"] == "Pedestrian"]
drv_row = rates[rates["person_type_clean"] == "Driver"]
if not ped_row.empty and not drv_row.empty and drv_row.iloc[0]["fatality_rate"] > 0:
    multiplier = ped_row.iloc[0]["fatality_rate"] / drv_row.iloc[0]["fatality_rate"]
    multiplier_text = f"about <strong style='color:#B91C1C;'>{multiplier:.0f}× higher</strong> than drivers"
else:
    multiplier_text = "substantially higher than drivers"

insight(
    f"Pedestrians and cyclists show a fatality rate {multiplier_text}. The bars look very different "
    "from each other — and that's the point. A driver in a crash overwhelmingly walks away. "
    "A pedestrian or cyclist often does not. This alone justifies treating vulnerable road users "
    "as a distinct policy population."
)

st.markdown("---")

# ── Vulnerable road user death share ─────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "How much of NYC's traffic death toll falls on people without cars?</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "Pedestrians and cyclists are the smaller groups in the data. But their share of citywide deaths "
    "is what matters for resource allocation — every percentage point above their share of "
    "involvement is evidence of disproportionate burden.</p>",
    unsafe_allow_html=True,
)

involvement_share = (totals_by_type / totals_by_type.sum() * 100).round(1)
death_share = (
    (killed_by_type / killed_by_type.sum() * 100).round(1)
    if killed_by_type.sum() > 0
    else killed_by_type * 0
)

share_df = pd.DataFrame(
    {
        "person_type": involvement_share.index,
        "Involvement share": involvement_share.values,
        "Death share": [death_share.get(pt, 0) for pt in involvement_share.index],
    }
).melt("person_type", var_name="metric", value_name="share")

share_color_scale = alt.Scale(
    domain=["Involvement share", "Death share"],
    range=[SIPA_BLUE, ACCENT_RED],
)

share_chart = (
    alt.Chart(share_df)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
        x=alt.X("share:Q", title="Share (%)"),
        y=alt.Y(
            "person_type:N",
            sort=["Pedestrian", "Cyclist", "Driver", "Occupant"],
            title=None,
        ),
        color=alt.Color(
            "metric:N",
            scale=share_color_scale,
            legend=alt.Legend(title=None, orient="top"),
        ),
        yOffset=alt.YOffset("metric:N"),
        tooltip=[
            alt.Tooltip("person_type:N", title="Group"),
            alt.Tooltip("metric:N", title="Metric"),
            alt.Tooltip("share:Q", title="Share", format=".1f"),
        ],
    )
    .properties(height=260)
)

st.altair_chart(share_chart, use_container_width=True)

formula_box(
    "Formula 2 — Disproportionality Index",
    "Disproportionality = ( Death Share % ÷ Involvement Share % )",
    "An index above 1.0 means the group dies at a higher rate than their crash exposure would predict. "
    "An index of 2.0 means double the expected death rate.",
)

# Compute the disproportionality index for pedestrians
if not ped_row.empty:
    ped_inv = involvement_share.get("Pedestrian", 0)
    ped_death = death_share.get("Pedestrian", 0) if killed_by_type.sum() > 0 else 0
    if ped_inv > 0:
        index = ped_death / ped_inv
        insight(
            f"Pedestrians make up <strong>{ped_inv:.1f}%</strong> of people involved in crashes "
            f"but <strong>{ped_death:.1f}%</strong> of deaths — a disproportionality index of "
            f"<strong style='color:#B91C1C;'>{index:.1f}</strong>. Numbers above 1.0 are the "
            "definition of an unequal burden. This is exactly the kind of gap a policy aimed at "
            "average drivers will fail to close."
        )

st.markdown("---")

# ── Safety equipment ─────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='font-family:JetBrains Mono,monospace;font-weight:600;color:#0F172A;'>"
    "Among drivers and occupants — does safety equipment change outcomes?</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#475569;font-size:0.93rem;line-height:1.7;'>"
    "For people who <em>are</em> in a vehicle, the question shifts: does what they do inside that "
    "vehicle affect their outcome? This is observational, not experimental — but the gap between "
    "groups is large enough to be informative.</p>",
    unsafe_allow_html=True,
)

safety_filtered = safety_df[
    safety_df["equipment"].isin(
        ["Seatbelt worn", "No safety equipment", "Airbag deployed", "Other equipment"]
    )
    & safety_df["outcome"].isin(["Killed", "Injured", "No injury"])
].copy()

safety_chart = (
    alt.Chart(safety_filtered)
    .mark_bar()
    .encode(
        x=alt.X(
            "people:Q",
            title="Share of people (%)",
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

insight(
    "People with no safety equipment show a markedly higher proportion of serious injuries and "
    "fatalities. Selection effects exist — higher-risk drivers may also be less likely to buckle up — "
    "but the gap is large enough that targeted seatbelt enforcement remains a high-return policy lever, "
    "particularly during late-night windows when impairment is more likely."
)

st.markdown("---")

# ── Page-level takeaway ──────────────────────────────────────────────────────
takeaway(
    "<strong style='color:#1c2536;'>1. Pedestrians and cyclists die at far higher rates than drivers — "
    "even though drivers vastly outnumber them in the data.</strong> "
    "Raw counts hide this. Per-involvement rates make it impossible to ignore.<br><br>"
    "<strong style='color:#1c2536;'>2. The disproportionality index quantifies the gap.</strong> "
    "Vulnerable road users die at multiples of their expected rate. Any policy framework should "
    "treat them as a distinct population with distinct interventions.<br><br>"
    "<strong style='color:#1c2536;'>3. For drivers, behavior matters — seatbelt enforcement still "
    "has measurable returns.</strong> Two policy fronts in parallel: street design for the unprotected, "
    "behavioral enforcement for the protected."
)

st.markdown("---")

with st.expander("Download underlying data"):
    st.download_button(
        label="Download person-type outcomes (CSV)",
        data=person_df.to_csv(index=False),
        file_name="who_bears_risk_outcomes.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download safety equipment outcomes (CSV)",
        data=safety_df.to_csv(index=False),
        file_name="who_bears_risk_safety_equipment.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download fatality rates by group (CSV)",
        data=rates.to_csv(index=False),
        file_name="who_bears_risk_rates.csv",
        mime="text/csv",
    )

elapsed = time.time() - start_time
st.caption(
    f"Loaded in {elapsed:.2f}s · Filters: {len(filters['person_types'])} person types · {filters['time_period']}"
)
