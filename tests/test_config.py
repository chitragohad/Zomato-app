"""Settings and deployment config tests."""

from src.config import Settings


class TestCorsOrigins:
    def test_default_local_origins(self):
        s = Settings(cors_origins="http://localhost:3000,http://127.0.0.1:3000")
        assert s.cors_origins_list == [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    def test_wildcard(self):
        s = Settings(cors_origins="*")
        assert s.cors_origins_list == ["*"]

    def test_strips_whitespace(self):
        s = Settings(cors_origins="https://a.vercel.app , https://b.vercel.app")
        assert s.cors_origins_list == [
            "https://a.vercel.app",
            "https://b.vercel.app",
        ]
