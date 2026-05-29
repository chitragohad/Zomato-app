"""Rule-based fallback ranker when LLM is unavailable."""

from __future__ import annotations

from src.ai.parser import format_estimated_cost
from src.domain.dedupe import dedupe_restaurants_by_name
from src.domain.display import format_restaurant_address
from src.models.preferences import UserPreferences
from src.models.recommendation import Recommendation, RecommendationResponse
from src.models.restaurant import Restaurant


class FallbackRanker:
    """Sort by rating/votes and generate template explanations."""

    def rank(
        self,
        candidates: list[Restaurant],
        preferences: UserPreferences,
        *,
        top_k: int = 5,
    ) -> RecommendationResponse:
        sorted_candidates = dedupe_restaurants_by_name(
            sorted(
                candidates,
                key=lambda r: (
                    r.rating if r.rating is not None else -1,
                    r.votes if r.votes is not None else 0,
                    r.name,
                ),
                reverse=True,
            )
        )[:top_k]

        cuisine_label = preferences.cuisine or "varied cuisine"
        recommendations: list[Recommendation] = []

        for i, restaurant in enumerate(sorted_candidates, start=1):
            explanation = (
                f"Highly rated {cuisine_label} option in {preferences.location} "
                f"within your {preferences.budget.value} budget."
            )
            if restaurant.rating is not None:
                explanation += f" Rating: {restaurant.rating}/5."

            recommendations.append(
                Recommendation(
                    rank=i,
                    restaurant_id=restaurant.id,
                    name=restaurant.name,
                    cuisine=", ".join(restaurant.cuisines) if restaurant.cuisines else "Unknown",
                    rating=restaurant.rating,
                    estimated_cost=format_estimated_cost(restaurant),
                    explanation=explanation,
                    location_detail=restaurant.location_detail,
                    address=format_restaurant_address(restaurant),
                )
            )

        summary = (
            f"Top picks in {preferences.location} based on rating and your filters "
            f"(rule-based ranking — LLM unavailable)."
        )

        return RecommendationResponse(
            summary=summary,
            recommendations=recommendations,
            used_fallback=True,
        )
