"""Phase 4 recommendation service integration tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.ai.client import GroqClient, get_llm_client, is_llm_available
from src.config import Settings
from src.domain.exceptions import EmptyFilterResultError
from src.models.preferences import UserPreferences
from src.models.recommendation import Recommendation, RecommendationResponse
from src.models.restaurant import BudgetTier, Restaurant
from src.services.recommendation import RecommendationService


def _restaurant(id_: str, name: str, rating: float = 4.5) -> Restaurant:
    return Restaurant(
        id=id_,
        name=name,
        city="Bangalore",
        cuisines=["Italian"],
        rating=rating,
        cost_for_two=600,
        budget_tier=BudgetTier.MEDIUM,
        votes=100,
    )


@pytest.fixture
def mock_repo_and_filter():
    """Service with mocked filter returning fixed candidates."""
    candidates = [_restaurant("a", "Alpha", 4.8), _restaurant("b", "Beta", 4.2)]

    mock_repo = MagicMock()
    mock_repo.is_loaded.return_value = True
    mock_repo.get_restaurant_count.return_value = 2
    mock_repo.get_cities.return_value = ["Bangalore"]

    mock_filter = MagicMock()
    mock_filter.filter.return_value = candidates

    return mock_repo, mock_filter, candidates


class TestGroqClient:
    def test_get_llm_client_returns_groq_by_default(self):
        settings = Settings(llm_provider="groq", llm_api_key="test-key")
        client = get_llm_client(settings)
        assert isinstance(client, GroqClient)

    def test_is_llm_available_requires_key_for_groq(self):
        assert is_llm_available(Settings(llm_provider="groq", llm_api_key="")) is False
        assert is_llm_available(Settings(llm_provider="groq", llm_api_key="gsk_x")) is True

    def test_is_llm_available_ollama_without_key(self):
        assert is_llm_available(Settings(llm_provider="ollama", llm_api_key="")) is True


class TestRecommendationService:
    def test_get_recommendations_with_mocked_engine(self, mock_repo_and_filter):
        mock_repo, mock_filter, candidates = mock_repo_and_filter

        mock_response = RecommendationResponse(
            summary="Great picks.",
            recommendations=[
                Recommendation(
                    rank=1,
                    restaurant_id="a",
                    name="Alpha",
                    cuisine="Italian",
                    rating=4.8,
                    estimated_cost="₹600 for two",
                    explanation="Top Italian choice in Bangalore.",
                )
            ],
            used_fallback=False,
        )
        mock_engine = MagicMock()
        mock_engine.recommend.return_value = mock_response

        service = RecommendationService(
            repository=mock_repo,
            filter_service=mock_filter,
            engine=mock_engine,
        )
        prefs = UserPreferences(location="Bangalore", cuisine="Italian")
        result = service.get_recommendations(prefs, top_k=1)

        mock_filter.filter.assert_called_once_with(prefs)
        mock_engine.recommend.assert_called_once()
        assert result.recommendations[0].name == "Alpha"

    def test_empty_filter_raises_without_llm_call(self, mock_repo_and_filter):
        mock_repo, mock_filter, _ = mock_repo_and_filter
        mock_filter.filter.side_effect = EmptyFilterResultError(
            UserPreferences(location="Bangalore", cuisine="Mexican")
        )
        mock_engine = MagicMock()

        service = RecommendationService(
            repository=mock_repo,
            filter_service=mock_filter,
            engine=mock_engine,
        )

        with pytest.raises(EmptyFilterResultError):
            service.get_recommendations(
                UserPreferences(location="Bangalore", cuisine="Mexican")
            )

        mock_engine.recommend.assert_not_called()

    def test_force_fallback_passed_to_engine(self, mock_repo_and_filter):
        mock_repo, mock_filter, candidates = mock_repo_and_filter
        mock_engine = MagicMock()
        mock_engine.recommend.return_value = RecommendationResponse(
            recommendations=[], used_fallback=True
        )

        service = RecommendationService(
            repository=mock_repo,
            filter_service=mock_filter,
            engine=mock_engine,
        )
        prefs = UserPreferences(location="Bangalore")
        service.get_recommendations(prefs, force_fallback=True)

        mock_engine.recommend.assert_called_once()
        call_kwargs = mock_engine.recommend.call_args[1]
        assert call_kwargs["force_fallback"] is True


@pytest.mark.skipif(
    not Settings().data_cache_path.exists(),
    reason="Requires ingested data/restaurants.parquet",
)
class TestRecommendationServiceIntegration:
    def test_end_to_end_fallback(self):
        service = RecommendationService()
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetTier.MEDIUM,
            cuisine="Italian",
            min_rating=4.0,
        )
        response = service.get_recommendations(prefs, top_k=3, force_fallback=True)
        assert len(response.recommendations) <= 3
        assert response.used_fallback is True
