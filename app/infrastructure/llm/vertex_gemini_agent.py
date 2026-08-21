"""LLMAgentPort'un Gemini implementasyonu (google-genai SDK, Gemini Enterprise
Agent Platform / eski adiyla Vertex AI uzerinden).

NOT: Ilk yazildiginda `vertexai.generative_models` (eski Vertex AI SDK) kullanilmisti,
ama o modul deprecated cikti (kaldirma tarihi gecmis durumda) -- google-genai SDK'ya
tasindik. Detay: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk

Yaklasim degismedi: Gemini'ye serbest SQL yazdirmak yerine, ApplianceDataRepositoryPort
uzerindeki iki metodu birer "tool" (function declaration) olarak taniyoruz. Gemini
hangi tool'u hangi parametrelerle cagiracagina karar veriyor, gercek sorguyu biz
(repository implementasyonu) calistiriyoruz -- guvenlik ve maliyet kontrolu bizde kaliyor.
Bu yuzden otomatik function-calling'i (SDK'nin kendi kendine tool calistirip donmesi)
bilerek kapattik, akisi elle yonetiyoruz.
"""

import dataclasses
from datetime import date

from google import genai
from google.genai import types

from app.application.ports import ApplianceDataRepositoryPort, LLMAgentPort
from app.domain.entities import AgentAnswer, DateRange
from app.domain.exceptions import UnsupportedQueryError

# Mock veri setiyle (scripts/generate_mock_usage_data.py) birebir uyumlu. Gercek
# sema gelince bu liste (ve InMemoryApplianceRepository yerine gecen BigQuery
# implementasyonu) guncellenecek.
APPLIANCE_TYPES = ["camasir_makinesi", "bulasik_makinesi", "buzdolabi", "firin", "klima"]

_MOST_USED_PROGRAM = types.FunctionDeclaration(
    name="most_used_program",
    description=(
        "Belirli bir beyaz esya tipinde, belirli bir tarih araliginda en cok kullanilan "
        "programlari kullanim sayisina gore azalan sirada dondurur."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "appliance_type": {"type": "string", "enum": APPLIANCE_TYPES},
            "start_date": {"type": "string", "description": "YYYY-MM-DD formatinda baslangic tarihi"},
            "end_date": {"type": "string", "description": "YYYY-MM-DD formatinda bitis tarihi"},
        },
        "required": ["appliance_type", "start_date", "end_date"],
    },
)

_MOST_PREFERRED_APPLIANCE = types.FunctionDeclaration(
    name="most_preferred_appliance",
    description=(
        "Belirli bir tarih araliginda en cok kullanilan (tercih edilen) beyaz esya "
        "tiplerini kullanim sayisina gore azalan sirada dondurur."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "start_date": {"type": "string", "description": "YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "YYYY-MM-DD"},
        },
        "required": ["start_date", "end_date"],
    },
)


class VertexGeminiAgentAdapter(LLMAgentPort):
    def __init__(
        self,
        project: str,
        location: str,
        repository: ApplianceDataRepositoryPort,
        model_name: str = "gemini-2.5-flash",
    ):
        self._client = genai.Client(enterprise=True, project=project, location=location)
        self._repository = repository
        self._model_name = model_name
        self._tool = types.Tool(function_declarations=[_MOST_USED_PROGRAM, _MOST_PREFERRED_APPLIANCE])
        self._config = types.GenerateContentConfig(
            tools=[self._tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            system_instruction=(
                "Sen Vestel beyaz esya kullanim verisi uzerinde soru cevaplayan bir "
                "asistansin. Sorulari elindeki tool'lari cagirarak cevapla, tool "
                "sonucunu Turkce, kisa ve net bir cumleyle ozetle.\n"
                "Elindeki tool'lar sadece cihaz tipi, program adi ve tarih araligina "
                "gore calisir. Soru sehir, enerji tuketimi, kullanim suresi gibi "
                "tool'larin kapsamadigi bir bilgiyi istiyorsa veya elindeki tool'larla "
                "cevaplanamiyorsa, tahmin/uydurma yapma -- bu veriye erisimin olmadigini "
                "acikca soyle.\n"
                f"Bugunun tarihi: {date.today().isoformat()}"
            ),
        )

    def answer_question(self, question: str) -> AgentAnswer:
        chat = self._client.chats.create(model=self._model_name, config=self._config)
        response = chat.send_message(question)

        function_calls = response.function_calls
        if not function_calls:
            return AgentAnswer(natural_language_answer=response.text)

        call = function_calls[0]
        try:
            tool_result = self._execute_tool(call.name, dict(call.args))
        except (UnsupportedQueryError, ValueError, KeyError):
            return AgentAnswer(
                natural_language_answer=(
                    "Bu soruyu elimdeki verilerle cevaplayamiyorum -- desteklenen "
                    "cihaz tipi ve tarih araligini kontrol edip tekrar sorabilir misin?"
                )
            )

        follow_up = chat.send_message(
            types.Part.from_function_response(name=call.name, response={"content": tool_result})
        )
        return AgentAnswer(natural_language_answer=follow_up.text, structured_data=tool_result)

    def _execute_tool(self, name: str, args: dict) -> list[dict]:
        if name == "most_used_program":
            date_range = DateRange(
                start=date.fromisoformat(args["start_date"]), end=date.fromisoformat(args["end_date"])
            )
            results = self._repository.most_used_program(args["appliance_type"], date_range)
            return [dataclasses.asdict(r) for r in results]

        if name == "most_preferred_appliance":
            date_range = DateRange(
                start=date.fromisoformat(args["start_date"]), end=date.fromisoformat(args["end_date"])
            )
            results = self._repository.most_preferred_appliance(date_range)
            return [dataclasses.asdict(r) for r in results]

        raise UnsupportedQueryError(f"Bilinmeyen tool: {name}")
