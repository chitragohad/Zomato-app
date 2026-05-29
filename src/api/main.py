"""FastAPI backend for restaurant recommendations."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.ai.client import is_llm_available
from src.config import get_settings
from src.domain.exceptions import EmptyFilterResultError, InvalidLocationError
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload restaurant data so Railway health checks pass immediately."""
    settings = get_settings()
    port = os.environ.get("PORT", "8000")
    cache = settings.data_cache_path.resolve()
    logger.info("API starting on port %s (Railway sets PORT; 8080 is normal)", port)
    logger.info("Data cache path: %s (exists=%s)", cache, cache.exists())

    if not cache.exists():
        logger.error(
            "Missing %s — commit data/restaurants.parquet or run ingest on build",
            cache,
        )
    else:
        try:
            service = get_service()
            logger.info(
                "Preloaded %d restaurants",
                service.repository.get_restaurant_count(),
            )
        except Exception:
            logger.exception("Failed to preload restaurant data")

    yield


_settings = get_settings()

app = FastAPI(
    title="Zomato AI Restaurant API",
    description="Backend API for AI-powered restaurant recommendations",
    version="1.0.0",
    lifespan=lifespan,
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


@app.get("/")
def root() -> dict:
    """Root route for platform probes and quick sanity checks."""
    return {"service": "Zomato AI Restaurant API", "health": "/health", "docs": "/docs"}


@app.get("/health")
def health():
    """
    Railway health check endpoint.

    Returns HTTP 200 only when restaurant data is loaded; 503 otherwise so
    failed deploys surface clearly in the Railway dashboard.
    """
    settings = get_settings()
    cache = settings.data_cache_path.resolve()
    if not cache.exists():
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": f"Restaurant cache not found at {cache}",
                "hint": "Ensure data/restaurants.parquet is in the repo or ingest runs on build",
            },
        )

    try:
        service = get_service()
        count = service.repository.get_restaurant_count()
        return {
            "status": "ok",
            "restaurants_loaded": count,
            "llm_provider": settings.llm_provider,
            "llm_available": is_llm_available(settings),
            "cache_path": str(cache),
            "port": os.environ.get("PORT"),
        }
    except Exception as exc:
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(exc)},
        )


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
