from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class BudgetTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Restaurant(BaseModel):
    id: str
    name: str
    city: str
    location_detail: Optional[str] = None
    cuisines: list[str] = Field(default_factory=list)
    rating: Optional[float] = None
    cost_for_two: Optional[int] = None
    budget_tier: Optional[BudgetTier] = None
    votes: Optional[int] = None
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
