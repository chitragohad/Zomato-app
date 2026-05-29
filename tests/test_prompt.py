"""Phase 3 prompt builder tests."""

from __future__ import annotations

import json

from src.ai.prompt import PromptBuilder, SYSTEM_PROMPT
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier


class TestPromptBuilder:
    def test_build_returns_system_and_user(self):
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetTier.MEDIUM,
            cuisine="Italian",
            min_rating=4.0,
            additional_preferences="family-friendly",
        )
        candidates = [{"id": "abc", "name": "Test", "cuisine": "Italian", "rating": 4.5}]
        messages = PromptBuilder.build(prefs, candidates, top_k=3)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_system_prompt_constraints(self):
        assert "ONLY" in SYSTEM_PROMPT
        assert "restaurant_id" in SYSTEM_PROMPT

    def test_user_message_contains_all_preferences(self):
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetTier.LOW,
            cuisine="Chinese",
            min_rating=3.5,
            additional_preferences="quick service",
        )
        messages = PromptBuilder.build(prefs, [{"id": "1", "name": "A"}], top_k=5)
        user = messages[1]["content"]

        assert "Bangalore" in user
        assert "low" in user
        assert "Chinese" in user
        assert "3.5" in user
        assert "quick service" in user
        assert "top 5" in user.lower()

    def test_candidates_in_user_message(self):
        prefs = UserPreferences(location="Delhi")
        candidates = [{"id": "x1", "name": "Spice Route"}]
        messages = PromptBuilder.build(prefs, candidates, top_k=2)
        assert "x1" in messages[1]["content"]
        assert "Spice Route" in messages[1]["content"]

    def test_json_repair_message(self):
        messages = PromptBuilder.build_json_repair_messages('{"broken":', top_k=3)
        assert "invalid JSON" in messages[1]["content"].lower() or "Invalid" in messages[1]["content"]
