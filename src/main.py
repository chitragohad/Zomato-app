"""CLI entry point for end-to-end recommendations (Phase 4)."""

from __future__ import annotations

import argparse
import logging
import sys

from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier
from src.services.recommendation import RecommendationService


def _configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_response(response) -> None:
    if response.summary:
        print(f"\n{response.summary}\n")

    if not response.recommendations:
        print("No recommendations returned.")
        return

    for rec in response.recommendations:
        rating_str = f"{rec.rating}/5" if rec.rating is not None else "N/A"
        print(f"#{rec.rank} {rec.name} — {rec.cuisine}")
        print(f"   Rating: {rating_str}  |  Cost: {rec.estimated_cost}")
        print(f"   {rec.explanation}\n")

    if response.used_fallback:
        print("(Rule-based fallback — Groq LLM was unavailable or failed)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Get AI-powered restaurant recommendations (Zomato dataset)"
    )
    parser.add_argument("--location", required=True, help="City, e.g. Bangalore")
    parser.add_argument(
        "--budget",
        default="medium",
        choices=["low", "medium", "high"],
        help="Budget tier",
    )
    parser.add_argument("--cuisine", default=None, help="Cuisine filter, e.g. Italian")
    parser.add_argument("--min-rating", type=float, default=0.0, help="Minimum rating 0-5")
    parser.add_argument(
        "--additional",
        default=None,
        help="Additional preferences, e.g. family-friendly",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of recommendations")
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Force rule-based ranking (skip Groq)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    try:
        preferences = UserPreferences(
            location=args.location,
            budget=BudgetTier(args.budget),
            cuisine=args.cuisine,
            min_rating=args.min_rating,
            additional_preferences=args.additional,
        )
    except Exception as exc:
        print(f"Invalid preferences: {exc}", file=sys.stderr)
        return 1

    try:
        service = RecommendationService()
        response = service.get_recommendations(
            preferences,
            top_k=args.top_k,
            force_fallback=args.fallback,
        )
        _print_response(response)
        return 0

    except InvalidLocationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except EmptyFilterResultError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        logging.exception("Recommendation failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
