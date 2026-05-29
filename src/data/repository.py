"""Restaurant data repository — load and query cached Parquet."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import Settings, get_settings
from src.domain.exceptions import DataLoadError
from src.models.restaurant import BudgetTier, Restaurant

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """Loads restaurant data from Parquet cache and exposes query helpers."""

    def __init__(self, cache_path: Optional[Path] = None, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()
        self._cache_path = cache_path or self._settings.data_cache_path
        self._df: Optional[pd.DataFrame] = None

    @property
    def cache_path(self) -> Path:
        return self._cache_path

    def is_loaded(self) -> bool:
        return self._df is not None

    def load(self, *, force_reload: bool = False) -> pd.DataFrame:
        if self._df is not None and not force_reload:
            return self._df

        if not self._cache_path.exists():
            raise DataLoadError(
                f"Restaurant cache not found at {self._cache_path}. "
                "Run: python -m src.data.loader --ingest"
            )

        logger.info("Loading restaurant cache from %s", self._cache_path)
        self._df = pd.read_parquet(self._cache_path)
        logger.info("Loaded %d restaurants", len(self._df))
        return self._df

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.load()

    def get_cities(self) -> list[str]:
        df = self.load()
        cities = sorted(df["city"].dropna().unique().tolist())
        return cities

    def _iter_cuisine_tokens(self, val) -> list[str]:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return []
        if isinstance(val, str):
            return [c.strip() for c in val.split(",") if c.strip()]
        if isinstance(val, (list, tuple)):
            return [str(c).strip() for c in val if str(c).strip()]
        # numpy ndarray from parquet
        try:
            return [str(c).strip() for c in val if str(c).strip()]
        except TypeError:
            return []

    def get_cuisines(self) -> list[str]:
        df = self.load()
        cuisines: set[str] = set()
        for val in df["cuisines"]:
            cuisines.update(self._iter_cuisine_tokens(val))
        return sorted(cuisines)

    def get_restaurant_count(self) -> int:
        return len(self.load())

    def to_restaurants(self, df: Optional[pd.DataFrame] = None) -> list[Restaurant]:
        source = df if df is not None else self.load()
        restaurants: list[Restaurant] = []

        for _, row in source.iterrows():
            budget = row.get("budget_tier")
            if budget is not None and not pd.isna(budget):
                budget = BudgetTier(str(budget))
            else:
                budget = None

            cuisines = self._iter_cuisine_tokens(row.get("cuisines"))

            restaurants.append(
                Restaurant(
                    id=str(row["id"]),
                    name=str(row["name"]),
                    city=str(row["city"]),
                    location_detail=row.get("location_detail") if pd.notna(row.get("location_detail")) else None,
                    cuisines=list(cuisines),
                    rating=float(row["rating"]) if pd.notna(row.get("rating")) else None,
                    cost_for_two=int(row["cost_for_two"]) if pd.notna(row.get("cost_for_two")) else None,
                    budget_tier=budget,
                    votes=int(row["votes"]) if pd.notna(row.get("votes")) else None,
                    raw_metadata=row.get("raw_metadata") if isinstance(row.get("raw_metadata"), dict) else {},
                )
            )

        return restaurants


@lru_cache(maxsize=1)
def get_repository() -> RestaurantRepository:
    """Singleton repository for app-wide use."""
    repo = RestaurantRepository()
    repo.load()
    return repo
