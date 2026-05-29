from src.domain.budget import BudgetMapper, assign_budget_tiers, compute_cost_percentiles
from src.domain.exceptions import (
    DataLoadError,
    DataValidationError,
    EmptyFilterResultError,
    InvalidLocationError,
)
from src.domain.serialize import serialize_candidates

__all__ = [
    "BudgetMapper",
    "FilterService",
    "EmptyFilterResultError",
    "InvalidLocationError",
    "DataLoadError",
    "DataValidationError",
    "serialize_candidates",
    "assign_budget_tiers",
    "compute_cost_percentiles",
    "normalize_location",
]


def __getattr__(name: str):
    if name == "FilterService":
        from src.domain.filter import FilterService
        return FilterService
    if name == "normalize_location":
        from src.domain.filter import normalize_location
        return normalize_location
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
