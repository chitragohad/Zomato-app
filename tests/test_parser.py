"""Phase 3 response parser tests."""

from __future__ import annotations

import json

import pytest

from src.ai.parser import ResponseParser, extract_json_text
from src.domain.exceptions import LLMParseError
from src.models.restaurant import BudgetTier, Restaurant


@pytest.fixture
def candidates() -> list[Restaurant]:
    return [
        Restaurant(
            id="id1",
            name="Italian Place",
            city="Bangalore",
            cuisines=["Italian"],
            rating=4.5,
            cost_for_two=800,
            budget_tier=BudgetTier.MEDIUM,
            votes=100,
        ),
        Restaurant(
            id="id2",
            name="South Spice",
            city="Bangalore",
            cuisines=["South Indian"],
            rating=4.0,
            cost_for_two=400,
            budget_tier=BudgetTier.LOW,
            votes=50,
        ),
    ]


@pytest.fixture
def parser() -> ResponseParser:
    return ResponseParser()


class TestExtractJson:
    def test_strips_markdown_fences(self):
        raw = '```json\n{"summary": "hi", "recommendations": []}\n```'
        assert extract_json_text(raw).startswith("{")

    def test_extracts_embedded_object(self):
        raw = 'Here is the result: {"recommendations": []} done'
        text = extract_json_text(raw)
        assert json.loads(text)["recommendations"] == []


class TestResponseParser:
    def test_parse_valid_response(self, parser, candidates):
        payload = {
            "summary": "Great Italian options in Bangalore.",
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "id1",
                    "name": "Italian Place",
                    "cuisine": "Italian",
                    "rating": 4.5,
                    "estimated_cost": "₹800 for two",
                    "explanation": "Perfect for your medium budget and Italian cuisine preference in Bangalore.",
                }
            ],
        }
        result = parser.parse(json.dumps(payload), candidates, top_k=5)
        assert result.summary is not None
        assert len(result.recommendations) == 1
        assert result.recommendations[0].restaurant_id == "id1"
        assert result.used_fallback is False

    def test_rejects_hallucinated_id(self, parser, candidates):
        payload = {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "fake-id",
                    "name": "Fake",
                    "cuisine": "X",
                    "estimated_cost": "₹100",
                    "explanation": "test",
                }
            ]
        }
        with pytest.raises(LLMParseError):
            parser.parse(json.dumps(payload), candidates)

    def test_invalid_json_raises(self, parser, candidates):
        with pytest.raises(LLMParseError):
            parser.parse("not json at all", candidates)

    def test_backfill_name_from_candidate(self, parser, candidates):
        payload = {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "id2",
                    "cuisine": "South Indian",
                    "estimated_cost": "₹400 for two",
                    "explanation": "Good South Indian match for Bangalore.",
                }
            ]
        }
        result = parser.parse(json.dumps(payload), candidates, top_k=5)
        assert result.recommendations[0].name == "South Spice"

    def test_empty_explanation_gets_template(self, parser, candidates):
        payload = {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "id1",
                    "name": "Italian Place",
                    "cuisine": "Italian",
                    "estimated_cost": "₹800",
                    "explanation": "",
                }
            ]
        }
        result = parser.parse(json.dumps(payload), candidates)
        assert len(result.recommendations[0].explanation) > 10

    def test_dedupe_duplicate_ids(self, parser, candidates):
        payload = {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "id1",
                    "name": "A",
                    "cuisine": "Italian",
                    "estimated_cost": "₹800",
                    "explanation": "First",
                },
                {
                    "rank": 2,
                    "restaurant_id": "id1",
                    "name": "A again",
                    "cuisine": "Italian",
                    "estimated_cost": "₹800",
                    "explanation": "Duplicate",
                },
            ]
        }
        result = parser.parse(json.dumps(payload), candidates, top_k=5)
        assert len(result.recommendations) == 1

    def test_caps_at_top_k(self, parser, candidates):
        payload = {
            "recommendations": [
                {
                    "rank": i,
                    "restaurant_id": rid,
                    "name": f"R{i}",
                    "cuisine": "X",
                    "estimated_cost": "₹100",
                    "explanation": f"Reason {i}",
                }
                for i, rid in enumerate(["id1", "id2"], start=1)
            ]
        }
        result = parser.parse(json.dumps(payload), candidates, top_k=1)
        assert len(result.recommendations) == 1
