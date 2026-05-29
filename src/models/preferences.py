from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.models.restaurant import BudgetTier

MAX_ADDITIONAL_PREFERENCES_LEN = 500


class UserPreferences(BaseModel):
    location: str = Field(..., min_length=1, description="City name, e.g. Bangalore")
    budget: BudgetTier = Field(default=BudgetTier.MEDIUM)
    cuisine: Optional[str] = Field(default=None, description="Cuisine type, e.g. Italian")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: Optional[str] = Field(
        default=None,
        description="Free-text preferences, e.g. family-friendly",
    )

    @field_validator("location")
    @classmethod
    def strip_location(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Location is required")
        return v

    @field_validator("cuisine")
    @classmethod
    def strip_cuisine(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v or v.lower() == "any":
            return None
        return v

    @field_validator("min_rating")
    @classmethod
    def clamp_rating(cls, v: float) -> float:
        return max(0.0, min(5.0, float(v)))

    @field_validator("additional_preferences")
    @classmethod
    def normalize_additional(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > MAX_ADDITIONAL_PREFERENCES_LEN:
            return v[:MAX_ADDITIONAL_PREFERENCES_LEN]
        return v
