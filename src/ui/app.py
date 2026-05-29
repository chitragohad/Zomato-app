"""
DineAI Restaurant Recommender — Streamlit UI.

Run: streamlit run src/ui/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.config import get_settings
from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.models.recommendation import RecommendationResponse
from src.services.recommendation import RecommendationService
from src.ui.components import (
    render_ai_summary,
    render_fallback_banner,
    render_recommendation_card,
    render_results_heading,
    render_sidebar_brand,
    render_welcome,
)
from src.ui.display import emit_html
from src.ui.helpers import build_preferences, format_location_line
from src.ui.theme import DINEAI_CSS
from src.ui.widgets import render_filter_controls

st.set_page_config(
    page_title="DineAI — Restaurant Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Loading restaurant data…")
def get_service() -> RecommendationService:
    settings = get_settings()
    if not settings.data_cache_path.exists():
        raise FileNotFoundError(
            f"Dataset cache not found at {settings.data_cache_path}. "
            "Run: python -m src.data.loader --ingest"
        )
    return RecommendationService(settings=settings)


def _inject_global_styles() -> None:
    st.markdown(f"<style>{DINEAI_CSS}</style>", unsafe_allow_html=True)


def _render_sidebar_shell() -> None:
    emit_html(render_sidebar_brand(), context=st.sidebar)


def _render_results(response: RecommendationResponse, *, city: str) -> None:
    if response.used_fallback:
        emit_html(render_fallback_banner())

    if response.summary:
        emit_html(render_ai_summary(response.summary))

    if not response.recommendations:
        st.warning("No recommendations returned.")
        return

    emit_html(render_results_heading(len(response.recommendations)))

    for rec in response.recommendations:
        location_line = format_location_line(
            address=rec.address,
            location_detail=rec.location_detail,
            city=city,
        )
        emit_html(render_recommendation_card(rec, location_line))


def main() -> None:
    _inject_global_styles()

    try:
        service = get_service()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"Failed to load restaurant data: {exc}")
        st.stop()

    _render_sidebar_shell()
    form = render_filter_controls(service)

    submitted = st.sidebar.button(
        "Get Recommendations",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.get("loading", False),
        key="dineai_submit",
    )

    if not submitted:
        st.session_state.loading = False
        emit_html(render_welcome())
        return

    if st.session_state.get("loading"):
        emit_html(
            render_ai_summary(
                "Finding your perfect spots — filtering candidates and ranking with AI…"
            )
        )
        return

    st.session_state.loading = True

    try:
        preferences = build_preferences(
            location=form["location"],
            budget_label=form["budget"],
            cuisine=form["cuisine"],
            min_rating=form["min_rating"],
            additional_preferences=form["additional"],
        )
    except Exception as exc:
        st.session_state.loading = False
        st.error(f"Invalid input: {exc}")
        return

    with st.spinner("Curating your recommendations…"):
        try:
            response = service.get_recommendations(
                preferences,
                top_k=form["top_k"],
                force_fallback=form["force_fallback"],
            )
            st.session_state.last_response = response
            _render_results(response, city=form["location"])

        except EmptyFilterResultError as exc:
            st.error(str(exc))
        except InvalidLocationError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(
                "Something went wrong while fetching recommendations. "
                "Please try again or relax your filters."
            )
            with st.expander("Technical details"):
                st.code(str(exc))
        finally:
            st.session_state.loading = False


if __name__ == "__main__":
    main()
