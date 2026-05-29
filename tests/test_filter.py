"""Phase 2 filter layer tests."""

from __future__ import annotations

import pandas as pd
import pytest

from src.config import Settings
from src.data.repository import RestaurantRepository
from src.domain.budget import BudgetMapper
from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.domain.filter import FilterService, normalize_location, _cuisine_matches
from src.domain.serialize import serialize_candidates
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier, Restaurant


@pytest.fixture
def filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "1",
                "name": "Italian Place",
                "city": "Bangalore",
                "location_detail": "Koramangala",
                "cuisines": ["Italian", "Pizza"],
                "rating": 4.5,
                "cost_for_two": 800,
                "budget_tier": "medium",
                "votes": 500,
                "raw_metadata": {},
            },
            {
                "id": "2",
                "name": "Budget South",
                "city": "Bangalore",
                "location_detail": "Indiranagar",
                "cuisines": ["South Indian"],
                "rating": 4.0,
                "cost_for_two": 300,
                "budget_tier": "low",
                "votes": 200,
                "raw_metadata": {},
            },
            {
                "id": "3",
                "name": "Fine Dine",
                "city": "Bangalore",
                "location_detail": "MG Road",
                "cuisines": ["Italian"],
                "rating": 4.8,
                "cost_for_two": 2000,
                "budget_tier": "high",
                "votes": 1000,
                "raw_metadata": {},
            },
            {
                "id": "4",
                "name": "Delhi Diner",
                "city": "Delhi",
                "location_detail": "CP",
                "cuisines": ["North Indian"],
                "rating": 4.2,
                "cost_for_two": 600,
                "budget_tier": "medium",
                "votes": 100,
                "raw_metadata": {},
            },
            {
                "id": "5",
                "name": "Unrated Cafe",
                "city": "Bangalore",
                "location_detail": "HSR",
                "cuisines": ["Italian"],
                "rating": None,
                "cost_for_two": 400,
                "budget_tier": "low",
                "votes": 10,
                "raw_metadata": {},
            },
        ]
    )


class MockRepository:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def get_cities(self) -> list[str]:
        return sorted(self._df["city"].dropna().unique().tolist())

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df

    def to_restaurants(self, df: pd.DataFrame | None = None) -> list[Restaurant]:
        source = df if df is not None else self._df
        results = []
        for _, row in source.iterrows():
            results.append(
                Restaurant(
                    id=str(row["id"]),
                    name=str(row["name"]),
                    city=str(row["city"]),
                    location_detail=row.get("location_detail"),
                    cuisines=list(row["cuisines"]),
                    rating=row["rating"] if pd.notna(row.get("rating")) else None,
                    cost_for_two=int(row["cost_for_two"]) if pd.notna(row.get("cost_for_two")) else None,
                    budget_tier=BudgetTier(str(row["budget_tier"])) if pd.notna(row.get("budget_tier")) else None,
                    votes=int(row["votes"]) if pd.notna(row.get("votes")) else None,
                )
            )
        return results


@pytest.fixture
def filter_service(filter_df) -> FilterService:
    settings = Settings(max_candidates=30)
    return FilterService(MockRepository(filter_df), settings=settings)


class TestNormalizeLocation:
    def test_bengaluru_alias(self):
        assert normalize_location("Bengaluru", ["Bangalore"]) == "Bangalore"

    def test_case_insensitive_known(self):
        assert normalize_location("bangalore", ["Bangalore"]) == "Bangalore"


class TestCuisineMatch:
    def test_substring(self):
        assert _cuisine_matches(["North Indian", "Chinese"], "indian") is True

    def test_partial_token(self):
        assert _cuisine_matches(["Italian", "Pizza"], "ital") is True

    def test_no_match(self):
        assert _cuisine_matches(["South Indian"], "Mexican") is False


class TestUserPreferences:
    def test_defaults(self):
        p = UserPreferences(location="Bangalore")
        assert p.budget == BudgetTier.MEDIUM
        assert p.min_rating == 0.0

    def test_reject_rating_above_five(self):
        with pytest.raises(Exception):
            UserPreferences(location="Bangalore", min_rating=6.0)

    def test_clamp_negative_rating_via_validation(self):
        with pytest.raises(Exception):
            UserPreferences(location="Bangalore", min_rating=-1.0)

    def test_truncate_additional(self):
        p = UserPreferences(location="Bangalore", additional_preferences="x" * 600)
        assert len(p.additional_preferences) == 500

    def test_any_cuisine_normalized_to_none(self):
        p = UserPreferences(location="Delhi", cuisine="Any")
        assert p.cuisine is None


class TestFilterServiceLocation:
    def test_case_insensitive(self, filter_service):
        prefs = UserPreferences(location="bangalore", budget=BudgetTier.MEDIUM)
        result = filter_service.filter(prefs)
        assert all(r.city == "Bangalore" for r in result)

    def test_invalid_city(self, filter_service):
        with pytest.raises(InvalidLocationError):
            filter_service.validate_location("Mumbaii")


class TestFilterServiceCuisine:
    def test_italian_filter(self, filter_service):
        prefs = UserPreferences(
            location="Bangalore",
            cuisine="Italian",
            budget=BudgetTier.MEDIUM,
            min_rating=0,
        )
        result = filter_service.filter(prefs)
        assert len(result) >= 1
        assert all(any("italian" in c.lower() for c in r.cuisines) for r in result)

    def test_skip_when_null(self, filter_service):
        prefs_no_cuisine = UserPreferences(
            location="Bangalore", cuisine=None, budget=BudgetTier.HIGH, min_rating=0
        )
        prefs_italian = UserPreferences(
            location="Bangalore", cuisine="Italian", budget=BudgetTier.HIGH, min_rating=0
        )
        assert len(filter_service.filter(prefs_no_cuisine)) >= len(
            filter_service.filter(prefs_italian)
        )


class TestFilterServiceRating:
    def test_min_rating_excludes_null_and_low(self, filter_service):
        prefs = UserPreferences(
            location="Bangalore",
            min_rating=4.0,
            budget=BudgetTier.LOW,
        )
        result = filter_service.filter(prefs)
        assert all(r.rating is not None and r.rating >= 4.0 for r in result)
        names = {r.name for r in result}
        assert "Unrated Cafe" not in names


class TestFilterServiceBudget:
    def test_medium_budget(self, filter_service):
        prefs = UserPreferences(
            location="Bangalore",
            cuisine="Italian",
            budget=BudgetTier.MEDIUM,
            min_rating=4.0,
        )
        result = filter_service.filter(prefs)
        assert len(result) == 1
        assert result[0].name == "Italian Place"

    def test_budget_mapper_skip_when_no_tiers(self):
        df = pd.DataFrame(
            [{"id": "1", "budget_tier": None}, {"id": "2", "budget_tier": None}]
        )
        out = BudgetMapper.apply(df, BudgetTier.HIGH)
        assert len(out) == 2


class TestFilterServiceCap:
    def test_cap_enforced(self, filter_df):
        settings = Settings(max_candidates=2)
        service = FilterService(MockRepository(filter_df), settings=settings)
        prefs = UserPreferences(location="Bangalore")
        result = service.filter(prefs)
        assert len(result) <= 2

    def test_sort_by_rating(self, filter_service):
        prefs = UserPreferences(location="Bangalore", budget=BudgetTier.HIGH)
        result = filter_service.filter(prefs)
        assert result[0].name == "Fine Dine"


class TestEmptyFilter:
    def test_raises_on_no_match(self, filter_service):
        prefs = UserPreferences(
            location="Bangalore",
            cuisine="Mexican",
            budget=BudgetTier.LOW,
        )
        with pytest.raises(EmptyFilterResultError) as exc_info:
            filter_service.filter(prefs)
        assert "Bangalore" in str(exc_info.value)


class TestSparseCityBudget:
    """Delhi/Mumbai have few rows; budget must use local percentiles or relax."""

    @pytest.fixture
    def sparse_repo(self) -> MockRepository:
        df = pd.DataFrame(
            [
                {
                    "id": "d1",
                    "name": "Delhi Spot A",
                    "city": "Delhi",
                    "location_detail": "CP",
                    "cuisines": ["North Indian"],
                    "rating": 4.0,
                    "cost_for_two": 350,
                    "budget_tier": "low",
                    "votes": 50,
                    "raw_metadata": {},
                },
                {
                    "id": "d2",
                    "name": "Delhi Spot B",
                    "city": "Delhi",
                    "location_detail": "Saket",
                    "cuisines": ["Chinese"],
                    "rating": 3.8,
                    "cost_for_two": 300,
                    "budget_tier": "low",
                    "votes": 30,
                    "raw_metadata": {},
                },
                {
                    "id": "m1",
                    "name": "Mumbai Spot",
                    "city": "Mumbai",
                    "location_detail": "Andheri",
                    "cuisines": ["Punjabi"],
                    "rating": 3.9,
                    "cost_for_two": 400,
                    "budget_tier": "medium",
                    "votes": 80,
                    "raw_metadata": {},
                },
            ]
        )
        return MockRepository(df)

    def test_delhi_high_budget_returns_results(self, sparse_repo):
        service = FilterService(sparse_repo, settings=Settings(max_candidates=10))
        prefs = UserPreferences(
            location="Delhi",
            budget=BudgetTier.HIGH,
            cuisine=None,
            min_rating=0,
        )
        result = service.filter(prefs)
        assert len(result) >= 1
        assert all(r.city == "Delhi" for r in result)

    def test_mumbai_high_budget_returns_results(self, sparse_repo):
        service = FilterService(sparse_repo, settings=Settings(max_candidates=10))
        prefs = UserPreferences(
            location="Mumbai",
            budget=BudgetTier.HIGH,
            cuisine=None,
            min_rating=0,
        )
        result = service.filter(prefs)
        assert len(result) >= 1
        assert result[0].city == "Mumbai"


class TestSerialize:
    def test_serialize_candidates(self, filter_service):
        prefs = UserPreferences(location="Bangalore", budget=BudgetTier.MEDIUM, cuisine="Italian")
        restaurants, payload = filter_service.filter_and_serialize(prefs)
        assert len(restaurants) == len(payload)
        assert payload[0]["id"] == restaurants[0].id
        assert "cuisine" in payload[0]


@pytest.mark.skipif(
    not Settings().data_cache_path.exists(),
    reason="Requires ingested data/restaurants.parquet",
)
class TestFilterIntegration:
    def test_bangalore_italian_medium_rating(self):
        repo = RestaurantRepository()
        service = FilterService(repo)
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetTier.MEDIUM,
            cuisine="Italian",
            min_rating=4.0,
        )
        result = service.filter(prefs)
        assert len(result) > 0
        assert len(result) <= service.max_candidates
        assert all(r.city == "Bangalore" for r in result)
        assert all(r.rating is not None and r.rating >= 4.0 for r in result)

    def test_bengaluru_alias(self):
        repo = RestaurantRepository()
        service = FilterService(repo)
        prefs = UserPreferences(location="Bengaluru", cuisine="Italian", min_rating=4.0)
        result = service.filter(prefs)
        assert len(result) > 0
