"""FastAPI backend for restaurant recommendations."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.ai.client import is_llm_available
from src.config import get_settings
from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation import RecommendationService

_settings = get_settings()

app = FastAPI(
    title="Zomato AI Restaurant API",
    description="Backend API for AI-powered restaurant recommendations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_service() -> RecommendationService:
    return RecommendationService()


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    try:
        service = get_service()
        count = service.repository.get_restaurant_count()
        return {
            "status": "ok",
            "restaurants_loaded": count,
            "llm_provider": settings.llm_provider,
            "llm_available": is_llm_available(settings),
            "cache_path": str(settings.data_cache_path),
        }
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


@app.get("/api/metadata/cities")
def list_cities() -> dict:
    return {"cities": get_service().get_cities()}


@app.get("/api/metadata/cuisines")
def list_cuisines() -> dict:
    return {"cuisines": get_service().get_cuisines()}


@app.post("/api/recommendations", response_model=RecommendationResponse)
def recommend(
    preferences: UserPreferences,
    top_k: Optional[int] = None,
    force_fallback: bool = False,
) -> RecommendationResponse:
    try:
        return get_service().get_recommendations(
            preferences,
            top_k=top_k,
            force_fallback=force_fallback,
        )
    except EmptyFilterResultError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidLocationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
