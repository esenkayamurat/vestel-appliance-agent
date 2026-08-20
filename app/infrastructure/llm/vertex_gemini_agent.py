"""LLMAgentPort'un Vertex AI Gemini implementasyonu.

Yaklasim: Gemini'ye serbest SQL yazdirmak yerine, ApplianceDataRepositoryPort
uzerindeki metodlari birer "tool" (function declaration) olarak tanitiyoruz.
Gemini hangi tool'u hangi parametrelerle cagiracagina karar veriyor, gercek
sorguyu biz (repository implementasyonu) calistiriyoruz -- guvenlik ve maliyet
kontrolu boylece bizde kaliyor.

Bu dosya, mock repository ile function-calling akisini erken denemek icin
gercek veri gelmeden de calistirilabilir; asil TODO Vertex AI SDK cagrisinin
(GenerativeModel + tool config) tamamlanmasi.
"""

from app.application.ports import ApplianceDataRepositoryPort, LLMAgentPort
from app.domain.entities import AgentAnswer


class VertexGeminiAgentAdapter(LLMAgentPort):
    def __init__(self, project: str, location: str, repository: ApplianceDataRepositoryPort):
        self._project = project
        self._location = location
        self._repository = repository
        # TODO: vertexai.init(project=project, location=location) + GenerativeModel
        # + tool/function declarations (most_used_program, most_preferred_appliance).

    def answer_question(self, question: str) -> AgentAnswer:
        raise NotImplementedError("Vertex AI Gemini function-calling entegrasyonu bekleniyor.")
