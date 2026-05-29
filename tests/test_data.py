"""Phase 1 data layer tests."""

import pandas as pd
import pytest

from src.data.preprocessor import (
    extract_city,
    parse_cost,
    parse_cuisines,
    parse_rating,
    preprocess_dataframe,
)
from src.domain.budget import assign_budget_tiers, compute_cost_percentiles, cost_to_budget_tier
from src.models.restaurant import BudgetTier


class TestParseRating:
    def test_standard_format(self):
        assert parse_rating("4.1/5") == pytest.approx(4.1)

    def test_missing_values(self):
        assert parse_rating("-") is None
        assert parse_rating(None) is None
        assert parse_rating("New") is None

    def test_clamps_high(self):
        assert parse_rating("6/5") == 5.0


class TestParseCost:
    def test_numeric_string(self):
        assert parse_cost("800") == 800

    def test_missing(self):
        assert parse_cost("") is None
        assert parse_cost(None) is None

    def test_zero_invalid(self):
        assert parse_cost("0") is None


class TestParseCuisines:
    def test_multiple_cuisines(self):
        assert parse_cuisines("North Indian, Chinese") == ["North Indian", "Chinese"]

    def test_trailing_comma(self):
        assert parse_cuisines("Cafe, Italian, ") == ["Cafe", "Italian"]

    def test_empty(self):
        assert parse_cuisines("") == []
        assert parse_cuisines(None) == []


class TestExtractCity:
    def test_bangalore_from_address(self):
        assert extract_city("123 Road, Bangalore") == "Bangalore"

    def test_bengaluru_alias(self):
        assert extract_city("456 Street, Bengaluru") == "Bangalore"

    def test_delhi(self):
        assert extract_city("1 Connaught Place, New Delhi") == "Delhi"


class TestPreprocessDataframe:
    def test_skips_invalid_rows(self, sample_raw_df):
        df = preprocess_dataframe(sample_raw_df)
        assert len(df) == 2

    def test_cuisine_tokenization(self, sample_processed_df):
        row = sample_processed_df.iloc[0]
        assert row["cuisines"] == ["North Indian", "Chinese"]

    def test_missing_cost_and_rating(self, sample_processed_df):
        row = sample_processed_df.iloc[1]
        assert row["rating"] is None or pd.isna(row["rating"])
        assert row["cost_for_two"] is None or pd.isna(row["cost_for_two"])

    def test_city_normalized(self, sample_processed_df):
        assert sample_processed_df.iloc[0]["city"] == "Bangalore"
        assert sample_processed_df.iloc[1]["city"] == "Bangalore"


class TestBudgetTier:
    def test_percentiles_deterministic(self):
        costs = pd.Series([100, 200, 300, 400, 500, 600, 700, 800, 900])
        p33, p66 = compute_cost_percentiles(costs)
        assert p33 < p66

    def test_tier_assignment(self):
        p33, p66 = 300.0, 600.0
        assert cost_to_budget_tier(200, p33, p66) == BudgetTier.LOW
        assert cost_to_budget_tier(450, p33, p66) == BudgetTier.MEDIUM
        assert cost_to_budget_tier(800, p33, p66) == BudgetTier.HIGH
        assert cost_to_budget_tier(None, p33, p66) is None

    def test_assign_budget_tiers_column(self, sample_processed_df):
        df = assign_budget_tiers(
            sample_processed_df.assign(cost_for_two=[800, 300])
        )
        assert df.loc[0, "budget_tier"] in (
            BudgetTier.HIGH,
            BudgetTier.MEDIUM,
            BudgetTier.LOW,
            "high",
            "medium",
            "low",
        )
        assert df.loc[0, "budget_tier"] == BudgetTier.HIGH or df.loc[0, "budget_tier"] == "high"
