"""Phase 3 recommendation engine tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.ai.engine import RecommendationEngine
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier, Restaurant


def _candidate(id_: str, rating: float) -> Restaurant:
    return Restaurant(
        id=id_,
        name=f"Restaurant {id_}",
        city="Bangalore",
        cuisines=["Italian"],
        rating=rating,
        cost_for_two=600,
        budget_tier=BudgetTier.MEDIUM,
    )


class TestRecommendationEngine:
    def test_force_fallback(self):
        engine = RecommendationEngine()
        prefs = UserPreferences(location="Bangalore", cuisine="Italian")
        candidates = [_candidate("a", 4.5), _candidate("b", 4.0)]
        result = engine.recommend(prefs, candidates, top_k=2, force_fallback=True)
        assert result.used_fallback is True
        assert len(result.recommendations) == 2

    @patch("src.ai.engine.is_llm_available", return_value=True)
    @patch("src.ai.engine.get_llm_client")
    def test_llm_success(self, mock_get_client, _mock_available):
        mock_client = MagicMock()
        mock_client.complete.return_value = """{
            "summary": "Top picks for you.",
            "recommendations": [{
                "rank": 1,
                "restaurant_id": "a",
                "name": "Restaurant a",
                "cuisine": "Italian",
                "rating": 4.5,
                "estimated_cost": "₹600 for two",
                "explanation": "Great Italian spot in Bangalore for your medium budget."
            }]
        }"""
        mock_get_client.return_value = mock_client

        engine = RecommendationEngine()
        prefs = UserPreferences(location="Bangalore", budget=BudgetTier.MEDIUM)
        result = engine.recommend(prefs, [_candidate("a", 4.5)], top_k=1)

        assert result.used_fallback is False
        assert result.recommendations[0].restaurant_id == "a"

    @patch("src.ai.engine.is_llm_available", return_value=True)
    @patch("src.ai.engine.get_llm_client")
    def test_llm_failure_uses_fallback(self, mock_get_client, _mock_available):
        from src.domain.exceptions import LLMProviderError

        mock_get_client.side_effect = LLMProviderError("API down")

        engine = RecommendationEngine()
        prefs = UserPreferences(location="Bangalore")
        candidates = [_candidate("a", 4.8), _candidate("b", 4.0)]
        result = engine.recommend(prefs, candidates, top_k=2)

        assert result.used_fallback is True
        assert result.recommendations[0].restaurant_id == "a"
