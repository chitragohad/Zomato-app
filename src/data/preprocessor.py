"""Normalize raw Zomato Hugging Face rows to canonical schema."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any, Optional

import pandas as pd

from src.domain.budget import assign_budget_tiers
from src.models.restaurant import BudgetTier

logger = logging.getLogger(__name__)

# Raw HF column names
COL_NAME = "name"
COL_ADDRESS = "address"
COL_LOCATION = "location"
COL_RATE = "rate"
COL_VOTES = "votes"
COL_CUISINES = "cuisines"
COL_COST = "approx_cost(for two people)"
COL_URL = "url"
COL_REST_TYPE = "rest_type"
COL_LISTED_CITY = "listed_in(city)"

CITY_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "banglore": "Bangalore",
    "bengalore": "Bangalore",
    "btm bangalore": "Bangalore",
}

MAJOR_CITIES = {
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "mumbai": "Mumbai",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "pune": "Pune",
    "kolkata": "Kolkata",
}

BANGALORE_KEYWORDS = ("bangalore", "bengaluru", "banglore", "bengalore", "banglore")


def parse_rating(value: Any) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().lower()
    if not text or text in ("-", "nan", "new", "none"):
        return None
    match = re.search(r"(\d+\.?\d*)", text)
    if not match:
        return None
    rating = float(match.group(1))
    if "/5" in text:
        return min(max(rating, 0.0), 5.0)
    if rating > 5:
        return min(rating / 10 if rating <= 10 else 5.0, 5.0)
    return min(max(rating, 0.0), 5.0)


def parse_cost(value: Any) -> Optional[int]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().lower()
    if not text or text in ("-", "nan"):
        return None
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return None
    cost = int(digits)
    return cost if cost > 0 else None


def parse_cuisines(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    parts = [p.strip() for p in str(value).split(",")]
    return [p for p in parts if p]


def extract_city(address: str, listed_city: Optional[str] = None) -> str:
    if not address or (isinstance(address, float) and pd.isna(address)):
        return "Unknown"

    addr_lower = str(address).lower()
    for keyword, city in MAJOR_CITIES.items():
        if keyword in addr_lower:
            return city

    for keyword in BANGALORE_KEYWORDS:
        if keyword in addr_lower:
            return "Bangalore"

    last_segment = str(address).split(",")[-1].strip()
    alias = CITY_ALIASES.get(last_segment.lower())
    if alias:
        return alias

    if last_segment.lower() in MAJOR_CITIES:
        return MAJOR_CITIES[last_segment.lower()]

    # Dataset is Bangalore-centric; area-only addresses default to Bangalore
    if len(last_segment) < 40:
        return "Bangalore"

    if listed_city and not pd.isna(listed_city):
        return "Bangalore"

    return "Unknown"


def make_restaurant_id(name: str, address: str, url: str = "") -> str:
    key = f"{name}|{address}|{url}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _row_to_record(row: pd.Series) -> Optional[dict[str, Any]]:
    name = row.get(COL_NAME)
    address = row.get(COL_ADDRESS)

    if name is None or pd.isna(name) or str(name).strip() == "":
        return None
    if address is None or pd.isna(address) or str(address).strip() == "":
        return None

    name = str(name).strip()
    address = str(address).strip()
    location_detail = row.get(COL_LOCATION)
    if location_detail is not None and not pd.isna(location_detail):
        location_detail = str(location_detail).strip()
    else:
        location_detail = None

    listed = row.get(COL_LISTED_CITY)
    city = extract_city(address, str(listed) if listed is not None else None)

    votes = row.get(COL_VOTES)
    if votes is not None and not pd.isna(votes):
        try:
            votes = int(votes)
        except (ValueError, TypeError):
            votes = None
    else:
        votes = None

    return {
        "id": make_restaurant_id(name, address, str(row.get(COL_URL, "") or "")),
        "name": name,
        "city": city,
        "location_detail": location_detail,
        "cuisines": parse_cuisines(row.get(COL_CUISINES)),
        "rating": parse_rating(row.get(COL_RATE)),
        "cost_for_two": parse_cost(row.get(COL_COST)),
        "votes": votes,
        "raw_metadata": {
            "url": row.get(COL_URL),
            "address": address,
            "rest_type": row.get(COL_REST_TYPE),
            "listed_in_city": listed,
        },
    }


def preprocess_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw HF dataframe to canonical schema."""
    records: list[dict[str, Any]] = []
    skipped = 0

    for _, row in raw_df.iterrows():
        record = _row_to_record(row)
        if record is None:
            skipped += 1
            continue
        records.append(record)

    if not records:
        raise ValueError("No valid restaurant records after preprocessing")

    logger.info("Preprocessing: kept %d rows, skipped %d", len(records), skipped)

    df = pd.DataFrame(records)
    df = assign_budget_tiers(df)

    # Store budget_tier as string for parquet compatibility
    df["budget_tier"] = df["budget_tier"].apply(
        lambda t: t.value if isinstance(t, BudgetTier) else t
    )

    return df


def log_dataset_stats(df: pd.DataFrame) -> None:
    """Log row counts, null rates, and metadata cardinalities."""
    n = len(df)
    logger.info("Dataset stats: %d restaurants", n)

    for col in ("name", "city", "rating", "cost_for_two"):
        if col in df.columns:
            null_pct = df[col].isna().mean() * 100
            logger.info("  %s null: %.2f%%", col, null_pct)

    if "city" in df.columns:
        logger.info("  unique cities: %d", df["city"].nunique())
        logger.info("  top cities: %s", df["city"].value_counts().head(5).to_dict())

    if "cuisines" in df.columns:
        all_cuisines: set[str] = set()
        for cuisines in df["cuisines"]:
            if isinstance(cuisines, list):
                all_cuisines.update(cuisines)
        logger.info("  unique cuisine tokens: %d", len(all_cuisines))

    if "budget_tier" in df.columns:
        logger.info("  budget_tier distribution: %s", df["budget_tier"].value_counts(dropna=False).to_dict())
