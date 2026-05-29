"""Orchestrates LLM recommendation: prompt → call → parse, with fallback."""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.ai.client import get_llm_client, is_llm_available
from src.ai.fallback import FallbackRanker
from src.ai.parser import ResponseParser
from src.ai.prompt import PromptBuilder
from src.config import Settings, get_settings
from src.domain.exceptions import LLMProviderError, LLMParseError
from src.domain.serialize import serialize_candidates
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Generate ranked recommendations from filtered candidates using LLM.

    Falls back to rule-based ranking when API key is missing or LLM fails.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        *,
        prompt_builder: Optional[PromptBuilder] = None,
        parser: Optional[ResponseParser] = None,
        fallback: Optional[FallbackRanker] = None,
    ):
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._parser = parser or ResponseParser()
        self._fallback = fallback or FallbackRanker()

    def recommend(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        *,
        top_k: Optional[int] = None,
        force_fallback: bool = False,
    ) -> RecommendationResponse:
        top_k = top_k or self._settings.top_k_results

        if not candidates:
            return RecommendationResponse(summary="No candidates to rank.", recommendations=[])

        if force_fallback or not is_llm_available(self._settings):
            logger.info(
                "Using fallback ranker (%s unavailable or forced)",
                self._settings.llm_provider,
            )
            return self._fallback.rank(candidates, preferences, top_k=top_k)

        serialized = serialize_candidates(candidates)
        messages = self._prompt_builder.build(preferences, serialized, top_k=top_k)

        try:
            client = get_llm_client(self._settings)
            raw = client.complete(messages, temperature=self._settings.llm_temperature)
            return self._parse_with_retry(raw, candidates, preferences, serialized, top_k)
        except (LLMProviderError, LLMParseError) as exc:
            logger.warning(
                "%s path failed, using fallback: %s",
                self._settings.llm_provider,
                exc,
            )
            return self._fallback.rank(candidates, preferences, top_k=top_k)

    def _parse_with_retry(
        self,
        raw: str,
        candidates: list[Restaurant],
        preferences: UserPreferences,
        serialized: list[dict[str, Any]],
        top_k: int,
    ) -> RecommendationResponse:
        try:
            return self._parser.parse(raw, candidates, top_k=top_k)
        except LLMParseError as first_error:
            logger.warning("Parse failed, attempting JSON repair: %s", first_error)
            try:
                client = get_llm_client(self._settings)
                repair_messages = self._prompt_builder.build_json_repair_messages(raw, top_k=top_k)
                repaired_raw = client.complete(
                    repair_messages,
                    temperature=self._settings.llm_temperature,
                )
                return self._parser.parse(repaired_raw, candidates, top_k=top_k)
            except (LLMProviderError, LLMParseError) as exc:
                raise LLMParseError(f"Parse and repair failed: {exc}") from exc
