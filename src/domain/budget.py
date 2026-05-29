"""Budget tier assignment and filtering."""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from src.models.restaurant import BudgetTier

logger = logging.getLogger(__name__)

# Fixed INR bands (fallback when percentiles unavailable)
FIXED_LOW_MAX = 500
FIXED_HIGH_MIN = 1501


def compute_cost_percentiles(costs: pd.Series) -> tuple[float, float]:
    """Return (p33, p66) for cost_for_two, clipping outliers at 1st–99th percentile."""
    valid = costs.dropna()
    if valid.empty:
        return float(FIXED_LOW_MAX), float(FIXED_HIGH_MIN)

    clipped = valid.clip(
        lower=valid.quantile(0.01),
        upper=valid.quantile(0.99),
    )
    return float(clipped.quantile(0.33)), float(clipped.quantile(0.66))


def cost_to_budget_tier(
    cost: Optional[float],
    p33: float,
    p66: float,
) -> Optional[BudgetTier]:
    if cost is None or pd.isna(cost):
        return None
    if cost <= p33:
        return BudgetTier.LOW
    if cost <= p66:
        return BudgetTier.MEDIUM
    return BudgetTier.HIGH


def assign_budget_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Add budget_tier column using dataset percentiles (33/66)."""
    out = df.copy()
    p33, p66 = compute_cost_percentiles(out["cost_for_two"])
    out["budget_tier"] = out["cost_for_two"].apply(
        lambda c: cost_to_budget_tier(c, p33, p66)
    )
    return out


def assign_budget_tiers_for_subset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recompute budget_tier from costs in the current candidate set.

    Uses city-local percentiles so sparse cities (Delhi, Mumbai) are not
    compared against Bangalore-wide cost bands.
    """
    if df.empty or "cost_for_two" not in df.columns:
        return df
    out = df.copy()
    p33, p66 = compute_cost_percentiles(out["cost_for_two"])
    tiers = out["cost_for_two"].apply(lambda c: cost_to_budget_tier(c, p33, p66))
    out["budget_tier"] = tiers.apply(
        lambda t: t.value if isinstance(t, BudgetTier) else t
    )
    return out


class BudgetMapper:
    """Maps user budget preference to restaurant budget_tier filtering."""

    @staticmethod
    def tier_value(budget: BudgetTier) -> str:
        return budget.value if isinstance(budget, BudgetTier) else str(budget)

    @staticmethod
    def apply(df: pd.DataFrame, budget: BudgetTier) -> pd.DataFrame:
        """
        Filter rows by budget_tier.

        If no rows have budget_tier assigned, skip filter (FILTER-05).
        """
        if df.empty:
            return df

        tier = BudgetMapper.tier_value(budget)
        has_any_tier = df["budget_tier"].notna().any()

        if not has_any_tier:
            logger.warning("Skipping budget filter: no budget_tier data in candidates")
            return df

        matched = df[df["budget_tier"] == tier]
        if matched.empty:
            logger.debug(
                "Budget filter '%s' removed all %d candidates",
                tier,
                len(df),
            )
        return matched
