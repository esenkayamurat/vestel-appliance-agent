"""Tek use case: kullanici sorusunu agent'a ilet, cevabi don.
Orkestrasyon (hangi tool cagrilacak, SQL nasil calisacak) bilerek burada degil,
LLMAgentPort implementasyonunun (infrastructure/llm) icinde -- use case sade kalsin diye."""

from dataclasses import dataclass

from app.application.ports import LLMAgentPort
from app.domain.entities import AgentAnswer


@dataclass
class AnswerUserQueryUseCase:
    agent: LLMAgentPort

    def execute(self, question: str) -> AgentAnswer:
        return self.agent.answer_question(question)
