"""Phase 5 UI helper tests."""

from src.models.restaurant import BudgetTier
from src.ui.helpers import (
    budget_label_to_tier,
    build_preferences,
    format_location_line,
    format_rating,
    rating_label_to_value,
    render_stars,
)


class TestBuildPreferences:
    def test_any_cuisine_becomes_none(self):
        p = build_preferences("Bangalore", "medium", "Any", 4.0, None)
        assert p.cuisine is None
        assert p.budget == BudgetTier.MEDIUM

    def test_with_cuisine_and_additional(self):
        p = build_preferences(
            "Delhi",
            "high",
            "Italian",
            3.5,
            "family-friendly",
        )
        assert p.location == "Delhi"
        assert p.cuisine == "Italian"
        assert p.additional_preferences == "family-friendly"


class TestFormatRating:
    def test_none(self):
        assert format_rating(None) == "Not rated"

    def test_value(self):
        assert format_rating(4.3) == "4.3/5"


class TestRenderStars:
    def test_full_rating(self):
        assert "★" in render_stars(4.5)

    def test_none(self):
        assert render_stars(None) == "—"


class TestFormatLocationLine:
    def test_detail_and_city(self):
        assert format_location_line(location_detail="Whitefield", city="Bangalore") == (
            "Whitefield, Bangalore"
        )

    def test_address_tail(self):
        addr = "120 A3, Hoodi, Whitefield, Bangalore"
        assert format_location_line(address=addr).endswith("Bangalore")


class TestRatingAndBudgetLabels:
    def test_rating_mapping(self):
        assert rating_label_to_value("4.5+") == 4.5
        assert rating_label_to_value("Any") == 0.0

    def test_budget_mid(self):
        assert budget_label_to_tier("Mid") == "medium"
