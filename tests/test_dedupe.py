"""Tests for restaurant name deduplication."""

from __future__ import annotations

import pandas as pd
import pytest

from src.config import Settings
from src.ai.fallback import FallbackRanker
from src.ai.parser import ResponseParser
from src.domain.dedupe import (
    dedupe_recommendations_by_name,
    dedupe_restaurants_by_name,
    normalize_name_key,
)
from src.domain.filter import FilterService
from tests.test_filter import MockRepository
from src.models.preferences import UserPreferences
from src.models.recommendation import Recommendation
from src.models.restaurant import BudgetTier, Restaurant


class TestNormalizeNameKey:
    def test_case_insensitive(self):
        assert normalize_name_key("Flechazo") == normalize_name_key("flechazo")

    def test_collapses_whitespace(self):
        assert normalize_name_key("  Asia   Kitchen  ") == normalize_name_key("asia kitchen")


class TestDedupeRestaurants:
    def test_keeps_first_highest_rated_order(self):
        restaurants = [
            Restaurant(id="1", name="Flechazo", city="Bangalore", rating=4.9, votes=100),
            Restaurant(id="2", name="Other", city="Bangalore", rating=4.5, votes=50),
            Restaurant(id="3", name="Flechazo", city="Bangalore", rating=4.0, votes=200),
        ]
        result = dedupe_restaurants_by_name(restaurants)
        assert len(result) == 2
        assert result[0].id == "1"
        assert result[1].name == "Other"


class TestDedupeRecommendations:
    def test_dedupes_and_renumbers_ranks(self):
        recs = [
            Recommendation(
                rank=1,
                restaurant_id="a",
                name="Flechazo",
                cuisine="Asian",
                rating=4.9,
                estimated_cost="₹1400",
                explanation="First",
            ),
            Recommendation(
                rank=2,
                restaurant_id="b",
                name="Other",
                cuisine="Asian",
                rating=4.8,
                estimated_cost="₹1200",
                explanation="Second",
            ),
            Recommendation(
                rank=3,
                restaurant_id="c",
                name="Flechazo",
                cuisine="Asian",
                rating=4.9,
                estimated_cost="₹1400",
                explanation="Duplicate",
            ),
        ]
        result = dedupe_recommendations_by_name(recs)
        assert len(result) == 2
        assert [r.name for r in result] == ["Flechazo", "Other"]
        assert [r.rank for r in result] == [1, 2]


class TestFilterDedupe:
    @pytest.fixture
    def duplicate_name_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "id": "dup-a",
                    "name": "Flechazo",
                    "city": "Bangalore",
                    "location_detail": "Whitefield",
                    "cuisines": ["Asian"],
                    "rating": 4.9,
                    "cost_for_two": 1400,
                    "budget_tier": "high",
                    "votes": 500,
                    "raw_metadata": {},
                },
                {
                    "id": "dup-b",
                    "name": "Flechazo",
                    "city": "Bangalore",
                    "location_detail": "Whitefield",
                    "cuisines": ["Asian"],
                    "rating": 4.5,
                    "cost_for_two": 1400,
                    "budget_tier": "high",
                    "votes": 100,
                    "raw_metadata": {},
                },
                {
                    "id": "unique",
                    "name": "Asia Kitchen",
                    "city": "Bangalore",
                    "location_detail": "Koramangala",
                    "cuisines": ["Asian"],
                    "rating": 4.8,
                    "cost_for_two": 1500,
                    "budget_tier": "high",
                    "votes": 300,
                    "raw_metadata": {},
                },
            ]
        )

    def test_filter_returns_unique_names(self, duplicate_name_df):
        service = FilterService(MockRepository(duplicate_name_df), settings=Settings(max_candidates=10))
        result = service.filter(
            UserPreferences(location="Bangalore", cuisine="Asian", budget=BudgetTier.HIGH)
        )
        names = [r.name.lower() for r in result]
        assert len(names) == len(set(names))
        flechazo = [r for r in result if r.name == "Flechazo"]
        assert len(flechazo) == 1
        assert flechazo[0].id == "dup-a"


class TestParserDedupe:
    def test_parser_dedupes_duplicate_names(self):
        candidates = [
            Restaurant(id="1", name="Flechazo", city="Bangalore", rating=4.9, votes=100),
            Restaurant(id="2", name="Flechazo", city="Bangalore", rating=4.5, votes=50),
            Restaurant(id="3", name="Asia Kitchen", city="Bangalore", rating=4.8, votes=80),
        ]
        payload = {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "1",
                    "name": "Flechazo",
                    "cuisine": "Asian",
                    "rating": 4.9,
                    "estimated_cost": "₹1400",
                    "explanation": "Great Asian food for your high budget in Bangalore.",
                },
                {
                    "rank": 2,
                    "restaurant_id": "3",
                    "name": "Asia Kitchen",
                    "cuisine": "Asian",
                    "rating": 4.8,
                    "estimated_cost": "₹1500",
                    "explanation": "Another strong Asian pick for Bangalore.",
                },
                {
                    "rank": 3,
                    "restaurant_id": "2",
                    "name": "Flechazo",
                    "cuisine": "Asian",
                    "rating": 4.5,
                    "estimated_cost": "₹1400",
                    "explanation": "Duplicate venue entry that should be dropped.",
                },
            ],
        }
        import json

        result = ResponseParser().parse(json.dumps(payload), candidates, top_k=5)
        names = [r.name for r in result.recommendations]
        assert names.count("Flechazo") == 1
        assert len(names) == len(set(n.lower() for n in names))


class TestFallbackDedupe:
    def test_fallback_unique_names(self):
        candidates = [
            Restaurant(id="1", name="Flechazo", city="Bangalore", rating=4.9, votes=100),
            Restaurant(id="2", name="Flechazo", city="Bangalore", rating=4.5, votes=50),
            Restaurant(id="3", name="Asia Kitchen", city="Bangalore", rating=4.8, votes=80),
        ]
        prefs = UserPreferences(location="Bangalore", budget=BudgetTier.HIGH, cuisine="Asian")
        result = FallbackRanker().rank(candidates, prefs, top_k=5)
        names = [r.name.lower() for r in result.recommendations]
        assert len(names) == len(set(names))
