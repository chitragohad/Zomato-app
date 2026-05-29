"""Tests for Streamlit HTML display helpers."""

from src.models.recommendation import Recommendation
from src.ui.components import render_ai_summary, render_recommendation_card
from src.ui.display import compact_html


class TestCompactHtml:
    def test_removes_newlines(self):
        raw = """
        <div>
            <span>Preferences</span>
        </div>
        """
        out = compact_html(raw)
        assert "\n" not in out
        assert "<div>" in out
        assert "Preferences" in out


class TestTextOnlyComponents:
    def test_no_material_symbols_in_summary(self):
        html = render_ai_summary("Test summary")
        assert "material-symbols" not in html
        assert "<img" not in html
        assert "Curated by AI" in html

    def test_no_images_or_icons_in_card(self):
        rec = Recommendation(
            rank=1,
            restaurant_id="id1",
            name="Test Place",
            cuisine="Italian, Pizza",
            rating=4.5,
            estimated_cost="₹800 for two",
            explanation="Great fit for your preferences in Bangalore.",
            address="Koramangala, Bangalore",
        )
        html = render_recommendation_card(rec, "Koramangala, Bangalore")
        assert "material-symbols" not in html
        assert "<img" not in html
        assert "Test Place" in html
        assert "AI Match:" in html
