"""Application service: orchestrates filter → Groq LLM → response."""

from __future__ import annotations

import logging
import time
from functools import lru_cache
from typing import Optional

from src.ai.engine import RecommendationEngine
from src.config import Settings, get_settings
from src.data.repository import RestaurantRepository
from src.domain.dedupe import dedupe_recommendations_by_name
from src.domain.display import format_restaurant_address
from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.domain.filter import FilterService
from src.models.preferences import UserPreferences
from src.models.recommendation import Recommendation, RecommendationResponse

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    End-to-end recommendation orchestration.

    Pipeline: load data → filter candidates → rank via Groq (or fallback).
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        *,
        repository: Optional[RestaurantRepository] = None,
        filter_service: Optional[FilterService] = None,
        engine: Optional[RecommendationEngine] = None,
    ):
        self._settings = settings or get_settings()
        self._repository = repository or RestaurantRepository(settings=self._settings)
        self._filter_service = filter_service or FilterService(
            self._repository, self._settings
        )
        self._engine = engine or RecommendationEngine(self._settings)
        self._ensure_data_loaded()

    def _ensure_data_loaded(self) -> None:
        if not self._repository.is_loaded():
            self._repository.load()
            logger.info(
                "Restaurant data ready: %d records",
                self._repository.get_restaurant_count(),
            )

    @property
    def repository(self) -> RestaurantRepository:
        return self._repository

    @property
    def filter_service(self) -> FilterService:
        return self._filter_service

    def get_cities(self) -> list[str]:
        return self._repository.get_cities()

    def get_cuisines(self) -> list[str]:
        return self._repository.get_cuisines()

    def _enrich_recommendation(self, rec: Recommendation) -> Recommendation:
        """Backfill name and address from dataset if missing (UI display guarantee)."""
        if rec.name and rec.address.strip():
            return rec

        df = self._repository.dataframe
        match = df[df["id"] == rec.restaurant_id]
        if match.empty:
            return rec.model_copy(
                update={
                    "name": rec.name or "Unknown restaurant",
                    "address": rec.address or "Address not available",
                }
            )

        restaurant = self._repository.to_restaurants(match)[0]
        return rec.model_copy(
            update={
                "name": rec.name or restaurant.name,
                "address": rec.address or format_restaurant_address(restaurant),
                "location_detail": rec.location_detail or restaurant.location_detail,
            }
        )

    def _enrich_response(
        self, response: RecommendationResponse, *, top_k: int
    ) -> RecommendationResponse:
        enriched = [self._enrich_recommendation(r) for r in response.recommendations]
        unique = dedupe_recommendations_by_name(enriched)[:top_k]
        return response.model_copy(update={"recommendations": unique})

    def get_recommendations(
        self,
        preferences: UserPreferences,
        *,
        top_k: Optional[int] = None,
        force_fallback: bool = False,
    ) -> RecommendationResponse:
        """
        Return ranked restaurant recommendations for user preferences.

        Raises:
            InvalidLocationError: Unknown city
            EmptyFilterResultError: No restaurants match filters (no LLM call)
        """
        top_k = top_k or self._settings.top_k_results
        total_start = time.perf_counter()

        filter_start = time.perf_counter()
        candidates = self._filter_service.filter(preferences)
        filter_elapsed = time.perf_counter() - filter_start

        logger.info(
            "Filter: %d candidates for %s in %.2fs (budget=%s, cuisine=%s, min_rating=%s)",
            len(candidates),
            preferences.location,
            filter_elapsed,
            preferences.budget.value,
            preferences.cuisine or "any",
            preferences.min_rating,
        )

        llm_start = time.perf_counter()
        response = self._engine.recommend(
            preferences,
            candidates,
            top_k=top_k,
            force_fallback=force_fallback,
        )
        llm_elapsed = time.perf_counter() - llm_start
        total_elapsed = time.perf_counter() - total_start

        response = self._enrich_response(response, top_k=top_k)

        provider = self._settings.llm_provider
        mode = "fallback" if response.used_fallback else provider
        logger.info(
            "Recommendations: %d results via %s in %.2fs (llm phase %.2fs, total %.2fs)",
            len(response.recommendations),
            mode,
            llm_elapsed,
            llm_elapsed,
            total_elapsed,
        )

        return response


@lru_cache(maxsize=1)
def get_recommendation_service() -> RecommendationService:
    """Singleton service with data loaded once."""
    return RecommendationService()
