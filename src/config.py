from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

GROQ_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["groq", "openai", "ollama"] = "groq"
    llm_api_key: str = ""
    llm_model: str = GROQ_DEFAULT_MODEL
    groq_base_url: str = GROQ_DEFAULT_BASE_URL

    data_cache_path: Path = Field(default=PROJECT_ROOT / "data" / "restaurants.parquet")
    hf_dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"

    max_candidates: int = 30
    top_k_results: int = 5

    # Comma-separated origins, or "*" for all (demo only)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    llm_temperature: float = 0.3
    llm_timeout: int = 60
    llm_max_retries: int = 1
    ollama_base_url: str = "http://localhost:11434"

    @property
    def data_cache_tmp_path(self) -> Path:
        return self.data_cache_path.with_suffix(".parquet.tmp")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS for FastAPI CORSMiddleware."""
        raw = self.cors_origins.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


def get_settings() -> Settings:
    return Settings()
