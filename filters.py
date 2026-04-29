"""
Shared sidebar filters used across all analytical pages.
Each page imports `render_filters()` and gets back a dict of filter values
that it can apply to its BigQuery queries (or pandas filtering).
"""

from datetime import date

import streamlit as st


BOROUGHS = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
PERSON_TYPES = ["Driver", "Occupant", "Pedestrian", "Cyclist"]
TIME_PERIODS = ["All hours", "Daytime (6am–10pm)", "Late night (10pm–6am)"]


def render_filters() -> dict:
    """Render the standard filter set in the sidebar and return chosen values."""
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-section-label">Filters</div>',
            unsafe_allow_html=True,
        )

        boroughs = st.multiselect(
            "Borough",
            options=BOROUGHS,
            default=BOROUGHS,
            help="Filter the analysis to specific NYC boroughs.",
        )

        person_types = st.multiselect(
            "Person type",
            options=PERSON_TYPES,
            default=PERSON_TYPES,
            help="Limit the analysis to specific road-user groups.",
        )

        time_period = st.radio(
            "Time period",
            options=TIME_PERIODS,
            index=0,
            help="Compare daytime patterns against late-night patterns.",
        )

        today = date.today()
        default_start = date(2026, 1, 1)
        date_range = st.slider(
            "Date range",
            min_value=date(2026, 1, 1),
            max_value=today,
            value=(default_start, today),
            format="MMM D",
            help="Restrict the analysis to a specific time window in 2026.",
        )

    # ── Apply sensible defaults if user clears a filter ───────────────────────
    if not boroughs:
        boroughs = BOROUGHS
    if not person_types:
        person_types = PERSON_TYPES

    return {
        "boroughs": boroughs,
        "person_types": person_types,
        "time_period": time_period,
        "date_start": date_range[0],
        "date_end": date_range[1],
    }


def time_period_sql_clause(time_period: str, hour_col: str = "hour") -> str:
    """Convert the time-period filter into a SQL WHERE fragment."""
    if time_period == "Daytime (6am–10pm)":
        return f"AND {hour_col} BETWEEN 6 AND 21"
    if time_period == "Late night (10pm–6am)":
        return f"AND ({hour_col} >= 22 OR {hour_col} < 6)"
    return ""


def render_context_bar(focus: str, filters: dict) -> None:
    """Render the breadcrumb-style context bar at the top of each analytical page."""
    boroughs_label = (
        "All boroughs"
        if len(filters["boroughs"]) == 5
        else ", ".join(filters["boroughs"])
    )

    st.markdown(
        f"""
        <div class="context-bar">
            <span class="context-label">Investigation Context</span>
            <strong>Focus:</strong> {focus} &nbsp;|&nbsp;
            <strong>Boroughs:</strong> {boroughs_label} &nbsp;|&nbsp;
            <strong>Period:</strong> {filters["time_period"]} &nbsp;|&nbsp;
            <strong>Dates:</strong> {filters["date_start"]:%b %-d} – {filters["date_end"]:%b %-d, %Y}
        </div>
        """,
        unsafe_allow_html=True,
    )
