"""Display / address formatting tests."""

from src.domain.display import format_restaurant_address
from src.models.restaurant import BudgetTier, Restaurant


def test_address_from_raw_metadata():
    r = Restaurant(
        id="1",
        name="Test",
        city="Bangalore",
        raw_metadata={"address": "123 MG Road, Koramangala, Bangalore"},
    )
    assert "MG Road" in format_restaurant_address(r)


def test_address_fallback_to_area_and_city():
    r = Restaurant(
        id="2",
        name="Test",
        city="Bangalore",
        location_detail="Whitefield",
    )
    assert format_restaurant_address(r) == "Whitefield, Bangalore"
