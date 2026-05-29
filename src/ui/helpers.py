"""UI helpers (pure functions for Streamlit app and tests)."""

from __future__ import annotations

from typing import Optional

from src.models.preferences import UserPreferences
from src.models.recommendation import Recommendation, RecommendationResponse
from src.models.restaurant import BudgetTier


def build_preferences(
    location: str,
    budget_label: str,
    cuisine: Optional[str],
    min_rating: float,
    additional_preferences: Optional[str],
) -> UserPreferences:
    """Build UserPreferences from form values."""
    cuisine_value = cuisine if cuisine and cuisine != "Any" else None
    return UserPreferences(
        location=location,
        budget=BudgetTier(budget_label.lower()),
        cuisine=cuisine_value,
        min_rating=min_rating,
        additional_preferences=additional_preferences or None,
    )


def format_rating(rating: Optional[float]) -> str:
    if rating is None:
        return "Not rated"
    return f"{rating:.1f}/5"


def render_stars(rating: Optional[float]) -> str:
    if rating is None:
        return "—"
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def format_location_line(
    *,
    address: str = "",
    location_detail: Optional[str] = None,
    city: Optional[str] = None,
) -> str:
    """Short location for cards (e.g. Whitefield, Bangalore)."""
    detail = (location_detail or "").strip()
    city_name = (city or "").strip()

    if detail and city_name:
        return f"{detail}, {city_name}"
    if detail:
        return detail

    addr = (address or "").strip()
    if not addr:
        return "Location not available"

    parts = [p.strip() for p in addr.split(",") if p.strip()]
    if len(parts) >= 2:
        return f"{parts[-2]}, {parts[-1]}"
    return addr[:80]


def rating_label_to_value(label: str) -> float:
    """Map sidebar rating chip labels to min_rating float."""
    mapping = {
        "Any": 0.0,
        "3.0+": 3.0,
        "4.0+": 4.0,
        "4.5+": 4.5,
    }
    return mapping.get(label, 0.0)


def budget_label_to_tier(label: str) -> str:
    """Map UI budget labels to BudgetTier values."""
    normalized = label.strip().lower()
    if normalized == "mid":
        return "medium"
    return normalized
