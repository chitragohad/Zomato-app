"""Phase 3 fallback ranker tests."""

from __future__ import annotations

from src.ai.fallback import FallbackRanker
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier, Restaurant


def _restaurant(id_: str, name: str, rating: float, votes: int) -> Restaurant:
    return Restaurant(
        id=id_,
        name=name,
        city="Bangalore",
        cuisines=["Italian"],
        rating=rating,
        cost_for_two=500,
        budget_tier=BudgetTier.MEDIUM,
        votes=votes,
    )


class TestFallbackRanker:
    def test_orders_by_rating_desc(self):
        candidates = [
            _restaurant("a", "Low", 3.5, 100),
            _restaurant("b", "High", 4.8, 10),
            _restaurant("c", "Mid", 4.2, 50),
        ]
        prefs = UserPreferences(location="Bangalore", cuisine="Italian")
        result = FallbackRanker().rank(candidates, prefs, top_k=3)

        assert result.used_fallback is True
        assert result.recommendations[0].name == "High"
        assert result.recommendations[1].name == "Mid"
        assert result.recommendations[2].name == "Low"

    def test_respects_top_k(self):
        candidates = [_restaurant(str(i), f"R{i}", 4.0 + i * 0.1, i) for i in range(5)]
        prefs = UserPreferences(location="Bangalore")
        result = FallbackRanker().rank(candidates, prefs, top_k=2)
        assert len(result.recommendations) == 2

    def test_explanation_mentions_preferences(self):
        candidates = [_restaurant("1", "Test", 4.5, 10)]
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetTier.MEDIUM,
            cuisine="Italian",
        )
        result = FallbackRanker().rank(candidates, prefs, top_k=1)
        exp = result.recommendations[0].explanation
        assert "Bangalore" in exp
        assert "medium" in exp
        assert "Italian" in exp

    def test_summary_present(self):
        candidates = [_restaurant("1", "Test", 4.0, 5)]
        prefs = UserPreferences(location="Bangalore")
        result = FallbackRanker().rank(candidates, prefs, top_k=1)
        assert result.summary is not None
        assert "fallback" in result.summary.lower() or "LLM" in result.summary
