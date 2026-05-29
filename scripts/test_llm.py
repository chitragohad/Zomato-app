#!/usr/bin/env python3
"""Standalone script to test LLM recommendation flow (Phase 3)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai.client import is_llm_available
from src.ai.engine import RecommendationEngine
from src.data.repository import RestaurantRepository
from src.domain.filter import FilterService
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier


def main() -> int:
    parser = argparse.ArgumentParser(description="Test LLM recommendation engine")
    parser.add_argument("--location", default="Bangalore")
    parser.add_argument("--budget", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", default="Italian")
    parser.add_argument("--min-rating", type=float, default=4.0)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Force rule-based fallback (no LLM call)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Alias for --fallback",
    )
    args = parser.parse_args()

    prefs = UserPreferences(
        location=args.location,
        budget=BudgetTier(args.budget),
        cuisine=args.cuisine or None,
        min_rating=args.min_rating,
        additional_preferences="family-friendly",
    )

    repo = RestaurantRepository()
    filter_service = FilterService(repo)
    candidates = filter_service.filter(prefs)

    print(f"Filtered {len(candidates)} candidates")
    print(f"LLM available: {is_llm_available()}")

    engine = RecommendationEngine()
    response = engine.recommend(
        prefs,
        candidates,
        top_k=args.top_k,
        force_fallback=args.fallback or args.mock,
    )

    print(f"\nUsed fallback: {response.used_fallback}")
    if response.summary:
        print(f"Summary: {response.summary}\n")

    for rec in response.recommendations:
        print(f"#{rec.rank} {rec.name} ({rec.rating}) — {rec.cuisine}")
        print(f"   Cost: {rec.estimated_cost}")
        print(f"   {rec.explanation}\n")

    print(json.dumps(response.model_dump(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
