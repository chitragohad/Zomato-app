"""Deduplicate restaurants and recommendations by name."""

from __future__ import annotations

from src.models.recommendation import Recommendation
from src.models.restaurant import Restaurant


def normalize_name_key(name: str) -> str:
    """Canonical key for restaurant name comparison."""
    return " ".join(str(name).lower().split())


def dedupe_restaurants_by_name(restaurants: list[Restaurant]) -> list[Restaurant]:
    """
    Remove duplicate restaurant names, keeping the first occurrence.

    Call after sorting by rating so the best-rated entry is kept.
    """
    seen: set[str] = set()
    unique: list[Restaurant] = []
    for restaurant in restaurants:
        key = normalize_name_key(restaurant.name)
        if key in seen:
            continue
        seen.add(key)
        unique.append(restaurant)
    return unique


def dedupe_recommendations_by_name(
    recommendations: list[Recommendation],
) -> list[Recommendation]:
    """Remove duplicate restaurant names from final results; re-number ranks."""
    seen: set[str] = set()
    unique: list[Recommendation] = []
    for rec in recommendations:
        key = normalize_name_key(rec.name)
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)

    for i, rec in enumerate(unique, start=1):
        unique[i - 1] = rec.model_copy(update={"rank": i})

    return unique
