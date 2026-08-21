"""Vertex AI Gemini function-calling akisini mock veriyle uctan uca dener.

DIKKAT: Bu script gercek Vertex AI Gemini API'sine istek atar (kucuk ama
gercek bir maliyeti olabilir). Bilerek Claude tarafindan degil, sen tarafindan
calistirilmasi icin yazildi.

On kosullar:
  1) gcloud auth application-default login   (daha once yapilmadiysa)
  2) GCP projende Vertex AI API'si acik olmali
  3) python scripts/generate_mock_usage_data.py   (data/mock_usage_data.csv yoksa)

Kullanim:
  export GCP_PROJECT=<proje-id>
  export GCP_REGION=europe-west1   # opsiyonel, varsayilan europe-west1
  python scripts/try_agent_locally.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.application.use_cases.answer_user_query import AnswerUserQueryUseCase
from app.infrastructure.data.in_memory_repository import InMemoryApplianceRepository
from app.infrastructure.llm.vertex_gemini_agent import VertexGeminiAgentAdapter

PROJECT = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION", "europe-west1")
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mock_usage_data.csv"

QUESTIONS = [
    "Son bir haftada en çok hangi çamaşır makinesi programı kullanıldı?",
    "Mart 2024'te en çok tercih edilen beyaz eşya hangisiydi?",
    # Kapsam disi sorular -- agent tool'lariyla cevaplanamayan bir soruda
    # tahmin/uydurma yapmiyor mu, gercekten "veriye erisimim yok" diyor mu?
    "İstanbul'da en çok hangi çamaşır makinesi programı kullanıldı?",
    "Klimaların ortalama enerji tüketimi ne kadar?",
    "En az kullanılan fırın programı hangisi?",
    "Genel olarak en çok kullanılan program nedir?",
]


def main():
    if not PROJECT:
        raise SystemExit("GCP_PROJECT ortam degiskeni set edilmemis.")
    if not DATA_PATH.exists():
        raise SystemExit(f"{DATA_PATH} bulunamadi. Once: python scripts/generate_mock_usage_data.py")

    repository = InMemoryApplianceRepository(DATA_PATH)
    agent = VertexGeminiAgentAdapter(project=PROJECT, location=REGION, repository=repository)
    use_case = AnswerUserQueryUseCase(agent=agent)

    for question in QUESTIONS:
        print(f"\nSoru: {question}")
        answer = use_case.execute(question)
        print(f"Cevap: {answer.natural_language_answer}")
        if answer.structured_data:
            print(f"Veri: {answer.structured_data}")


if __name__ == "__main__":
    main()
