"""Serialize restaurant candidates for LLM prompt injection."""

from __future__ import annotations

from typing import Any

from src.models.restaurant import Restaurant


def serialize_candidate(restaurant: Restaurant) -> dict[str, Any]:
    """Compact dict for a single restaurant (prompt payload)."""
    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "cuisine": ", ".join(restaurant.cuisines) if restaurant.cuisines else "Unknown",
        "rating": restaurant.rating,
        "cost_for_two": restaurant.cost_for_two,
        "location_detail": restaurant.location_detail,
        "budget_tier": restaurant.budget_tier.value if restaurant.budget_tier else None,
    }


def serialize_candidates(restaurants: list[Restaurant]) -> list[dict[str, Any]]:
    """Serialize a list of restaurants for LLM prompts."""
    return [serialize_candidate(r) for r in restaurants]
