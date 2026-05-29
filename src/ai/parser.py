"""Parse and validate LLM JSON responses."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from pydantic import ValidationError

from src.domain.dedupe import dedupe_recommendations_by_name
from src.domain.display import format_restaurant_address
from src.domain.exceptions import LLMParseError
from src.models.recommendation import Recommendation, RecommendationResponse
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


def extract_json_text(raw: str) -> str:
    """Strip markdown fences and extract JSON object from LLM output."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def format_estimated_cost(restaurant: Restaurant) -> str:
    if restaurant.cost_for_two is not None:
        return f"₹{restaurant.cost_for_two} for two"
    return "Cost not available"


class ResponseParser:
    """Validates LLM JSON and joins results to candidate restaurants."""

    def parse(
        self,
        raw_response: str,
        candidates: list[Restaurant],
        *,
        top_k: int = 5,
    ) -> RecommendationResponse:
        candidate_map = {r.id: r for r in candidates}
        valid_ids = set(candidate_map.keys())

        try:
            data = json.loads(extract_json_text(raw_response))
        except json.JSONDecodeError as exc:
            raise LLMParseError(f"Invalid JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise LLMParseError("Response must be a JSON object")

        raw_recs = data.get("recommendations", [])
        if not isinstance(raw_recs, list):
            raise LLMParseError("'recommendations' must be a list")

        recommendations: list[Recommendation] = []
        seen_ids: set[str] = set()

        for item in raw_recs:
            rec = self._parse_item(item, candidate_map, valid_ids, seen_ids)
            if rec is not None:
                recommendations.append(rec)

        if not recommendations:
            raise LLMParseError("No valid recommendations after parsing (hallucinated or empty IDs)")

        recommendations.sort(key=lambda r: r.rank)
        recommendations = dedupe_recommendations_by_name(recommendations)
        recommendations = recommendations[:top_k]

        # Re-number ranks after dedupe + cap
        for i, rec in enumerate(recommendations, start=1):
            recommendations[i - 1] = rec.model_copy(update={"rank": i})

        summary = data.get("summary")
        if summary is not None and not isinstance(summary, str):
            summary = str(summary)

        return RecommendationResponse(
            summary=summary,
            recommendations=recommendations,
            used_fallback=False,
        )

    def _parse_item(
        self,
        item: Any,
        candidate_map: dict[str, Restaurant],
        valid_ids: set[str],
        seen_ids: set[str],
    ) -> Optional[Recommendation]:
        if not isinstance(item, dict):
            return None

        restaurant_id = str(item.get("restaurant_id", "")).strip()
        if not restaurant_id or restaurant_id not in valid_ids:
            logger.warning("Dropping hallucinated or unknown restaurant_id: %s", restaurant_id)
            return None
        if restaurant_id in seen_ids:
            return None
        seen_ids.add(restaurant_id)

        source = candidate_map[restaurant_id]
        name = str(item.get("name") or source.name)
        cuisine = str(item.get("cuisine") or ", ".join(source.cuisines) or "Unknown")

        rating = item.get("rating")
        if rating is not None:
            try:
                rating = float(rating)
            except (TypeError, ValueError):
                rating = source.rating
        else:
            rating = source.rating

        estimated_cost = str(item.get("estimated_cost") or format_estimated_cost(source))
        explanation = str(item.get("explanation") or "").strip()
        if not explanation:
            explanation = (
                f"Matches your preferences for {source.city} "
                f"with {source.budget_tier.value if source.budget_tier else 'flexible'} budget."
            )

        rank = item.get("rank", len(seen_ids))
        try:
            rank = int(rank)
        except (TypeError, ValueError):
            rank = len(seen_ids)

        return Recommendation(
            rank=rank,
            restaurant_id=restaurant_id,
            name=name,
            cuisine=cuisine,
            rating=rating,
            estimated_cost=estimated_cost,
            explanation=explanation,
            location_detail=source.location_detail,
            address=format_restaurant_address(source),
        )
