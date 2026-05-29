"""Sidebar filter widgets with accessible contrast (Streamlit 1.50+)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.config import get_settings
from src.ui.helpers import budget_label_to_tier, rating_label_to_value

BUDGET_OPTIONS = ("Low", "Mid", "High")
RATING_OPTIONS = ("Any", "3.0+", "4.0+", "4.5+")


def _segmented(
    label: str,
    options: tuple[str, ...],
    *,
    default: str,
    key: str,
    container: Any = None,
) -> str:
    """Segmented control with readable selected/unselected states."""
    ctx = container or st.sidebar
    selected = ctx.segmented_control(
        label,
        options=list(options),
        default=default,
        key=key,
    )
    return selected if selected is not None else default


def render_filter_controls(service: Any, *, container: Any = None) -> dict:
    """
    Render sidebar preference inputs.

    Returns dict of form values (not including submit state).
    """
    ctx = container or st.sidebar
    cities = service.get_cities()
    default_city = "Bangalore" if "Bangalore" in cities else (cities[0] if cities else "")

    ctx.selectbox(
        "Location",
        options=cities,
        index=cities.index(default_city) if default_city in cities else 0,
        key="dineai_location",
    )

    budget_label = _segmented(
        "Budget",
        BUDGET_OPTIONS,
        default="High",
        key="dineai_budget_seg",
        container=ctx,
    )

    cuisines = ["Any"] + service.get_cuisines()
    if "dineai_cuisine" not in st.session_state:
        st.session_state.dineai_cuisine = "Any"
    ctx.selectbox("Cuisine", options=cuisines, key="dineai_cuisine")

    min_rating_label = _segmented(
        "Minimum Rating",
        RATING_OPTIONS,
        default="Any",
        key="dineai_min_rating_seg",
        container=ctx,
    )

    ctx.text_area(
        "Additional preferences",
        placeholder="e.g. family-friendly, quick service, rooftop",
        height=72,
        key="dineai_additional",
    )

    top_k = ctx.slider(
        "Recommendations count",
        min_value=1,
        max_value=10,
        value=get_settings().top_k_results,
        key="dineai_top_k",
    )

    return {
        "location": st.session_state.dineai_location,
        "budget": budget_label_to_tier(budget_label),
        "cuisine": st.session_state.dineai_cuisine,
        "min_rating": rating_label_to_value(min_rating_label),
        "additional": (st.session_state.dineai_additional or "").strip() or None,
        "top_k": top_k,
        "force_fallback": False,
    }
