"""Groq client unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.ai.client import GroqClient, get_llm_client
from src.config import Settings


class TestGroqClient:
    @patch("src.ai.client._chat_completions")
    def test_complete_delegates_with_groq_base_url(self, mock_chat):
        mock_chat.return_value = '{"recommendations": []}'
        settings = Settings(
            llm_provider="groq",
            llm_api_key="gsk_test",
            groq_base_url="https://api.groq.com/openai/v1",
        )
        client = GroqClient(settings)
        messages = [{"role": "user", "content": "test"}]
        result = client.complete(messages, temperature=0.2)

        assert result == '{"recommendations": []}'
        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs["base_url"] == "https://api.groq.com/openai/v1"
        assert call_kwargs["provider_name"] == "Groq"

    def test_factory_default_is_groq(self):
        settings = Settings(llm_provider="groq", llm_api_key="key")
        assert isinstance(get_llm_client(settings), GroqClient)
