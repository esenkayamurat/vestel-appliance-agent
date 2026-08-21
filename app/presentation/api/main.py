"""Presentation katmani: HTTP giris noktasi. Sadece istek/cevap donusumu ve
dependency wiring yapar -- is mantigi burada yok, hepsi application/infrastructure'da.

Veri kaynagi DATA_SOURCE ortam degiskeniyle seciliyor ("memory" | "bigquery").
Gercek BigQuery semasi mentorden gelene kadar BigQueryApplianceRepository stub
oldugu (NotImplementedError firlatiyor) icin varsayilan "memory" -- boylece
servis mock veriyle ayaga kalkip demo edilebiliyor. Gercek sema gelince
DATA_SOURCE=bigquery ile tek satir degisiklikle gecis yapilacak.
"""

import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from app.application.use_cases.answer_user_query import AnswerUserQueryUseCase
from app.infrastructure.data.bigquery_repository import BigQueryApplianceRepository
from app.infrastructure.data.in_memory_repository import InMemoryApplianceRepository
from app.infrastructure.llm.vertex_gemini_agent import VertexGeminiAgentAdapter

app = FastAPI(title="Vestel Agentic Appliance Insights")

PROJECT = os.environ.get("GCP_PROJECT", "")
REGION = os.environ.get("GCP_REGION", "europe-west1")
DATA_SOURCE = os.environ.get("DATA_SOURCE", "memory")

if DATA_SOURCE == "bigquery":
    DATASET = os.environ.get("BQ_DATASET", "")
    TABLE = os.environ.get("BQ_TABLE", "")
    _repository = BigQueryApplianceRepository(project=PROJECT, dataset=DATASET, table=TABLE)
elif DATA_SOURCE == "memory":
    MOCK_DATA_PATH = Path(
        os.environ.get(
            "MOCK_DATA_PATH", Path(__file__).resolve().parents[3] / "data" / "mock_usage_data.csv"
        )
    )
    _repository = InMemoryApplianceRepository(MOCK_DATA_PATH)
else:
    raise SystemExit(f"Bilinmeyen DATA_SOURCE: {DATA_SOURCE!r} (memory | bigquery olmali)")

_agent = VertexGeminiAgentAdapter(project=PROJECT, location=REGION, repository=_repository)
_use_case = AnswerUserQueryUseCase(agent=_agent)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def query(request: QueryRequest):
    answer = _use_case.execute(request.question)
    return {
        "answer": answer.natural_language_answer,
        "data": answer.structured_data,
    }
