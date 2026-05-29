from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.models.preferences import UserPreferences


class DataLoadError(Exception):
    """Failed to download or load restaurant data."""


class DataValidationError(Exception):
    """Ingest produced no valid restaurant records."""


class InvalidLocationError(Exception):
    """User-provided location is not in the dataset."""

    def __init__(self, location: str, known_cities: list[str], suggestion: Optional[str] = None):
        self.location = location
        self.known_cities = known_cities
        self.suggestion = suggestion
        hint = f" Did you mean '{suggestion}'?" if suggestion else ""
        super().__init__(
            f"Unknown location '{location}'. "
            f"Available cities: {', '.join(known_cities)}.{hint}"
        )


class EmptyFilterResultError(Exception):
    """No restaurants match the given filters."""

    def __init__(
        self,
        preferences: UserPreferences,
        suggestions: Optional[list[str]] = None,
    ):
        self.preferences = preferences
        self.suggestions = suggestions or [
            "Lower minimum rating",
            "Try a different cuisine or leave cuisine blank",
            "Switch to a broader budget tier",
        ]
        cuisine = preferences.cuisine or "any"
        message = (
            f"No restaurants found in {preferences.location} matching:\n"
            f"  • Cuisine: {cuisine}\n"
            f"  • Budget: {preferences.budget.value}\n"
            f"  • Minimum rating: {preferences.min_rating}\n\n"
            "Suggestions:\n"
            + "\n".join(f"  • {s}" for s in self.suggestions)
        )
        super().__init__(message)


class LLMProviderError(Exception):
    """LLM API call failed after retries."""


class LLMParseError(Exception):
    """Failed to parse LLM response as valid recommendations JSON."""
