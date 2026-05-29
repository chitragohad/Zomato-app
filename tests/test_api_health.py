"""FastAPI health and Railway deploy behavior tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

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
        assert "llm_provider" in body
        assert "cache_path" in body

    def test_health_503_when_cache_missing(self, client):
        missing = Path("/nonexistent/zomato-cache.parquet")
        mock_path = MagicMock()
        mock_path.resolve.return_value = missing

        with patch("src.api.main.get_settings") as mock_settings:
            settings = mock_settings.return_value
            settings.data_cache_path = mock_path
            settings.llm_provider = "groq"

            response = client.get("/health")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "unhealthy"
        assert "not found" in body["error"].lower()
        assert "restaurants.parquet" in body["hint"] or "parquet" in body["hint"].lower()

    def test_health_503_when_service_fails_after_cache_exists(self, client):
        resolved = MagicMock()
        resolved.exists.return_value = True
        mock_path = MagicMock()
        mock_path.resolve.return_value = resolved

        with (
            patch("src.api.main.get_settings") as mock_settings,
            patch("src.api.main.get_service", side_effect=RuntimeError("parquet corrupt")),
        ):
            settings = mock_settings.return_value
            settings.data_cache_path = mock_path
            settings.llm_provider = "groq"

            response = client.get("/health")

        assert response.status_code == 503
        assert response.json()["status"] == "unhealthy"
        assert "parquet corrupt" in response.json()["error"]

    def test_health_includes_port_env_when_set(self, client, monkeypatch):
        monkeypatch.setenv("PORT", "8080")
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["port"] == "8080"

    def test_root_returns_service_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert body["service"] == "Zomato AI Restaurant API"
        assert body["health"] == "/health"
        assert body["docs"] == "/docs"


class TestRunApiEntrypoint:
    def test_run_api_reads_port_from_environment(self, monkeypatch):
        import os

        import run_api

        monkeypatch.setenv("PORT", "8080")
        with patch.object(run_api.uvicorn, "run") as mock_run:
            port = int(os.environ.get("PORT", "8000"))
            run_api.uvicorn.run(
                "src.api.main:app",
                host="0.0.0.0",
                port=port,
                log_level="info",
            )

        assert mock_run.call_args.kwargs["host"] == "0.0.0.0"
        assert mock_run.call_args.kwargs["port"] == 8080

    def test_run_api_defaults_to_8000_without_port(self, monkeypatch):
        import os

        import run_api

        monkeypatch.delenv("PORT", raising=False)
        with patch.object(run_api.uvicorn, "run") as mock_run:
            port = int(os.environ.get("PORT", "8000"))
            run_api.uvicorn.run("src.api.main:app", host="0.0.0.0", port=port)

        assert mock_run.call_args.kwargs["port"] == 8000
