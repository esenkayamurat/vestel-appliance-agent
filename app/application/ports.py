"""Application katmani, disariya sadece bu soyut arayuzler (port) uzerinden baglanir.
Infrastructure katmanindaki somut siniflar (VertexGeminiAgentAdapter,
BigQueryApplianceRepository) bu port'lari implemente eder. Boylece use case'ler
gercek Vertex AI / BigQuery'ye dokunmadan, sahte (mock) implementasyonlarla test edilebilir.
"""

from abc import ABC, abstractmethod

from app.domain.entities import AgentAnswer, ApplianceUsageResult, DateRange, ProgramUsageResult


class ApplianceDataRepositoryPort(ABC):
    """Gercek veri kaynagina (BigQuery) erisimi soyutlar.

    NOT: Bu iki metod, mentorden gelen ornek sorulardan (son bir haftada en cok
    kullanilan program / en cok tercih edilen beyaz esya) turetildi. Gercek sema
    gelince metod imzalari buyuk ihtimalle genisleyecek, degismeyecek olan sey
    use case'lerin bu port'a bagimli olmasi.
    """

    @abstractmethod
    def most_used_program(
        self, appliance_type: str, date_range: DateRange
    ) -> list[ProgramUsageResult]:
        raise NotImplementedError

    @abstractmethod
    def most_preferred_appliance(self, date_range: DateRange) -> list[ApplianceUsageResult]:
        raise NotImplementedError


class LLMAgentPort(ABC):
    """Agent motorunu (Vertex AI Gemini) soyutlar. Use case, hangi modelin
    kullanildigini bilmez; sadece bir soru sorar, bir AgentAnswer alir."""

    @abstractmethod
    def answer_question(self, question: str) -> AgentAnswer:
        raise NotImplementedError
