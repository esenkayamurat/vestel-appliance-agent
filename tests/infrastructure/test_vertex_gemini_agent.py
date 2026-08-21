from types import SimpleNamespace
from unittest.mock import MagicMock

from app.infrastructure.llm.vertex_gemini_agent import VertexGeminiAgentAdapter


class _FailingRepository:
    def most_used_program(self, appliance_type, date_range):
        raise ValueError("beklenmeyen deger")

    def most_preferred_appliance(self, date_range):
        raise ValueError("beklenmeyen deger")


def _adapter_with_fake_chat(repository, function_calls):
    adapter = VertexGeminiAgentAdapter(project="fake-project", location="europe-west1", repository=repository)

    fake_response = SimpleNamespace(function_calls=function_calls, text="serbest metin cevap")
    fake_chat = MagicMock()
    fake_chat.send_message.return_value = fake_response
    adapter._client = MagicMock()
    adapter._client.chats.create.return_value = fake_chat
    return adapter


def test_tool_execution_failure_returns_graceful_fallback_instead_of_raising():
    call = SimpleNamespace(
        name="most_used_program",
        args={"appliance_type": "camasir_makinesi", "start_date": "2024-01-01", "end_date": "2024-01-31"},
    )
    adapter = _adapter_with_fake_chat(_FailingRepository(), function_calls=[call])

    answer = adapter.answer_question("hangi program en cok kullanildi?")

    assert "cevaplayamiyorum" in answer.natural_language_answer
    assert answer.structured_data is None


def test_unknown_tool_name_returns_graceful_fallback_instead_of_raising():
    call = SimpleNamespace(name="baska_bir_tool", args={})
    adapter = _adapter_with_fake_chat(_FailingRepository(), function_calls=[call])

    answer = adapter.answer_question("alakasiz bir soru")

    assert "cevaplayamiyorum" in answer.natural_language_answer
    assert answer.structured_data is None
