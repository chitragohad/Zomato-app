"""Display helpers for recommendation output."""

from __future__ import annotations

from src.models.restaurant import Restaurant


def format_restaurant_address(restaurant: Restaurant) -> str:
    """Full address string for UI — prefer raw address, else area + city."""
    raw = restaurant.raw_metadata or {}
    address = raw.get("address")
    if address and str(address).strip():
        return str(address).strip()

    parts: list[str] = []
    if restaurant.location_detail:
        parts.append(str(restaurant.location_detail).strip())
    if restaurant.city and restaurant.city not in parts:
        parts.append(str(restaurant.city).strip())

    return ", ".join(parts) if parts else "Address not available"
