"""Filter restaurants by user preferences."""

from __future__ import annotations

import logging
from difflib import get_close_matches
from typing import Optional

import pandas as pd

from src.config import Settings, get_settings
from src.data.preprocessor import CITY_ALIASES
from src.data.repository import RestaurantRepository
from src.domain.budget import BudgetMapper, assign_budget_tiers_for_subset
from src.domain.dedupe import dedupe_restaurants_by_name
from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.domain.serialize import serialize_candidates
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


def normalize_location(location: str, known_cities: Optional[list[str]] = None) -> str:
    """Normalize user location to canonical city name."""
    stripped = location.strip()
    alias = CITY_ALIASES.get(stripped.lower())
    if alias:
        return alias

    if known_cities:
        lower_map = {c.lower(): c for c in known_cities}
        if stripped.lower() in lower_map:
            return lower_map[stripped.lower()]

    return stripped.title() if stripped.islower() else stripped


def _cuisine_matches(cuisines_val, query: str) -> bool:
    """Case-insensitive token/substring match for cuisine filter."""
    query = query.strip().lower()
    if not query:
        return True

    tokens: list[str] = []
    if cuisines_val is None or (isinstance(cuisines_val, float) and pd.isna(cuisines_val)):
        return False
    if isinstance(cuisines_val, str):
        tokens = [c.strip() for c in cuisines_val.split(",") if c.strip()]
    elif isinstance(cuisines_val, (list, tuple)):
        tokens = [str(c).strip() for c in cuisines_val if str(c).strip()]
    else:
        try:
            tokens = [str(c).strip() for c in cuisines_val if str(c).strip()]
        except TypeError:
            return False

    for token in tokens:
        t_lower = token.lower()
        if query in t_lower or t_lower in query:
            return True
    return False


class FilterService:
    """
    Deterministic filter pipeline: location → cuisine → rating → budget → sort → cap.
    """

    def __init__(
        self,
        repository: RestaurantRepository,
        settings: Optional[Settings] = None,
    ):
        self._repository = repository
        self._settings = settings or get_settings()
        self._max_candidates = self._settings.max_candidates

    @property
    def max_candidates(self) -> int:
        return self._max_candidates

    def validate_location(self, location: str) -> str:
        """Normalize and validate location against dataset cities."""
        known = self._repository.get_cities()
        normalized = normalize_location(location, known)

        if normalized in known:
            return normalized

        # Case-insensitive match
        lower_map = {c.lower(): c for c in known}
        if normalized.lower() in lower_map:
            return lower_map[normalized.lower()]

        suggestion = None
        close = get_close_matches(location, known, n=1, cutoff=0.6)
        if close:
            suggestion = close[0]

        raise InvalidLocationError(location, known, suggestion)

    def _filter_location(self, df: pd.DataFrame, city: str) -> pd.DataFrame:
        return df[df["city"].str.lower() == city.lower()]

    def _filter_cuisine(self, df: pd.DataFrame, cuisine: Optional[str]) -> pd.DataFrame:
        if not cuisine:
            return df
        mask = df["cuisines"].apply(lambda val: _cuisine_matches(val, cuisine))
        return df[mask]

    def _filter_rating(self, df: pd.DataFrame, min_rating: float) -> pd.DataFrame:
        if min_rating <= 0:
            return df
        # Null ratings are below any positive threshold (FILTER-10)
        return df[df["rating"].notna() & (df["rating"] >= min_rating)]

    def _dedupe_dataframe_by_name(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep one row per restaurant name (best row first — call after sort)."""
        before = len(df)
        out = df.copy()
        out["_name_key"] = out["name"].astype(str).str.lower().str.strip()
        out = out.drop_duplicates(subset=["_name_key"], keep="first").drop(columns=["_name_key"])
        dropped = before - len(out)
        if dropped:
            logger.debug("Deduped %d duplicate restaurant names from candidates", dropped)
        return out

    def _sort_and_cap(self, df: pd.DataFrame) -> pd.DataFrame:
        sorted_df = df.sort_values(
            by=["rating", "votes", "name"],
            ascending=[False, False, True],
            na_position="last",
        )
        sorted_df = self._dedupe_dataframe_by_name(sorted_df)
        if len(sorted_df) > self._max_candidates:
            logger.debug(
                "Capping candidates from %d to %d",
                len(sorted_df),
                self._max_candidates,
            )
        return sorted_df.head(self._max_candidates)

    def filter_dataframe(self, preferences: UserPreferences) -> pd.DataFrame:
        """Run full filter pipeline on DataFrame without raising on empty."""
        city = self.validate_location(preferences.location)
        df = self._repository.dataframe.copy()

        df = self._filter_location(df, city)
        logger.debug("After location filter: %d rows", len(df))

        df = self._filter_cuisine(df, preferences.cuisine)
        logger.debug("After cuisine filter: %d rows", len(df))

        df = self._filter_rating(df, preferences.min_rating)
        logger.debug("After rating filter: %d rows", len(df))

        before_budget = df
        df = BudgetMapper.apply(df, preferences.budget)
        logger.debug("After budget filter (global tiers): %d rows", len(df))

        # Sparse cities: re-tier using local cost percentiles before giving up
        if df.empty and not before_budget.empty and len(before_budget) <= 25:
            local = assign_budget_tiers_for_subset(before_budget)
            df = BudgetMapper.apply(local, preferences.budget)
            logger.debug("After budget filter (city-local tiers): %d rows", len(df))

        if df.empty and not before_budget.empty:
            logger.info(
                "Budget '%s' removed all %d candidates for %s; returning matches without budget filter",
                preferences.budget.value,
                len(before_budget),
                preferences.location,
            )
            df = before_budget

        return self._sort_and_cap(df)

    def filter(self, preferences: UserPreferences) -> list[Restaurant]:
        """
        Filter restaurants by preferences.

        Raises:
            InvalidLocationError: Unknown city
            EmptyFilterResultError: Zero matches after filtering
        """
        result_df = self.filter_dataframe(preferences)

        if result_df.empty:
            raise EmptyFilterResultError(preferences)

        restaurants = self._repository.to_restaurants(result_df)
        restaurants = dedupe_restaurants_by_name(restaurants)
        logger.info(
            "Filter returned %d unique candidates for %s (max %d)",
            len(restaurants),
            preferences.location,
            self._max_candidates,
        )
        return restaurants

    def filter_and_serialize(
        self, preferences: UserPreferences
    ) -> tuple[list[Restaurant], list[dict]]:
        """Filter and return restaurants plus serialized prompt payload."""
        restaurants = self.filter(preferences)
        return restaurants, serialize_candidates(restaurants)
