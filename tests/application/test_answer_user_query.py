"""Clean architecture'in kazandirdigi sey: use case'i gercek Vertex AI/BigQuery'ye
dokunmadan, sahte bir LLMAgentPort implementasyonuyla test edebiliyoruz."""

from app.application.ports import LLMAgentPort
from app.application.use_cases.answer_user_query import AnswerUserQueryUseCase
from app.domain.entities import AgentAnswer


class FakeAgent(LLMAgentPort):
    def answer_question(self, question: str) -> AgentAnswer:
        return AgentAnswer(natural_language_answer=f"echo: {question}")


def test_use_case_delegates_to_agent():
    use_case = AnswerUserQueryUseCase(agent=FakeAgent())

    result = use_case.execute("test sorusu")

    assert result.natural_language_answer == "echo: test sorusu"
