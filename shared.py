"""
Shared utilities — BigQuery client, Altair theme, formula box helper.
"""

import altair as alt
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT_ID = "sipa-adv-c-sparkly-pickle"

# ── SIPA blue palette ────────────────────────────────────────────────────────
SIPA_BLUE = "#6F9FCF"
SIPA_BLUE_DARK = "#4A7FB5"
SIPA_BLUE_LIGHT = "#C9DDEF"
ACCENT_AMBER = "#D97706"
ACCENT_GREEN = "#15803D"
ACCENT_RED = "#B91C1C"
NEUTRAL_GREY = "#94A3B8"


@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


# ── Light Altair theme ───────────────────────────────────────────────────────
@alt.theme.register("sipa_light", enable=True)
def sipa_light():
    return {
        "config": {
            "background": "#FFFFFF",
            "view": {"stroke": "transparent"},
            "axis": {
                "gridColor": "#E2E8F0",
                "domainColor": "#CBD5E1",
                "tickColor": "#CBD5E1",
                "labelColor": "#64748B",
                "titleColor": "#334155",
                "labelFont": "Inter, sans-serif",
                "titleFont": "Inter, sans-serif",
                "labelFontSize": 11,
                "titleFontSize": 12,
                "titleFontWeight": 500,
            },
            "legend": {
                "labelColor": "#475569",
                "titleColor": "#1c2536",
                "labelFont": "Inter, sans-serif",
                "titleFont": "Inter, sans-serif",
                "labelFontSize": 11,
                "titleFontSize": 11,
                "titleFontWeight": 600,
            },
            "title": {
                "color": "#0F172A",
                "font": "JetBrains Mono, monospace",
                "fontSize": 13,
                "fontWeight": 600,
            },
            "range": {
                "category": [
                    SIPA_BLUE,
                    SIPA_BLUE_DARK,
                    ACCENT_AMBER,
                    ACCENT_GREEN,
                    NEUTRAL_GREY,
                ],
                "ramp": [
                    "#EBF2F9",
                    "#C9DDEF",
                    "#A0BFE0",
                    "#6F9FCF",
                    "#4A7FB5",
                    "#2C5A8F",
                ],
            },
        }
    }


def formula_box(label: str, formula: str, plain_explanation: str = "") -> None:
    """Render a formula in a styled monospace box with optional plain-language explanation."""
    extra = (
        f"<div style='font-family:Inter,sans-serif;font-size:0.83rem;"
        f"color:#64748B;margin-top:0.5rem;line-height:1.6;'>{plain_explanation}</div>"
        if plain_explanation
        else ""
    )
    st.markdown(
        f"""
        <div class="formula-box">
            <span class="formula-label">{label}</span>
            {formula}
            {extra}
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(text: str, label: str = "Key Insight") -> None:
    """Render a styled insight box."""
    st.markdown(
        f"""
        <div class="insight-box">
            <strong style="color:#4A7FB5;">{label}</strong><br>{text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def takeaway(
    text: str, label: str = "🎯 What you should take away from this page"
) -> None:
    """Render a styled takeaway box."""
    st.markdown(
        f"""
        <div class="takeaway-box">
            <strong style="color:#4A7FB5;">{label}</strong><br><br>{text}
        </div>
        """,
        unsafe_allow_html=True,
    )
