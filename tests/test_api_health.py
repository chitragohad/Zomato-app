"""FastAPI health and Railway deploy behavior tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    def test_health_ok_when_data_loaded(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["restaurants_loaded"] > 0

    def test_health_503_when_cache_missing(self, client):
        with patch("src.api.main.get_settings") as mock_settings:
            from pathlib import Path

            settings = mock_settings.return_value
            settings.data_cache_path.resolve.return_value = Path("/nonexistent/cache.parquet")
            settings.data_cache_path.exists.return_value = False
            settings.llm_provider = "groq"

            response = client.get("/health")

        assert response.status_code == 503
        assert response.json()["status"] == "unhealthy"

    def test_root_returns_service_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["health"] == "/health"
