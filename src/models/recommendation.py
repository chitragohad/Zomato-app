from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    rank: int = Field(..., ge=1)
    restaurant_id: str
    name: str
    cuisine: str
    rating: Optional[float] = None
    estimated_cost: str
    explanation: str
    location_detail: Optional[str] = None
    address: str = ""


class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    used_fallback: bool = False
