"""Presentation katmani: HTTP giris noktasi. Sadece istek/cevap donusumu ve
dependency wiring yapar -- is mantigi burada yok, hepsi application/infrastructure'da."""

import os

from fastapi import FastAPI
from pydantic import BaseModel

from app.application.use_cases.answer_user_query import AnswerUserQueryUseCase
from app.infrastructure.data.bigquery_repository import BigQueryApplianceRepository
from app.infrastructure.llm.vertex_gemini_agent import VertexGeminiAgentAdapter

app = FastAPI(title="Vestel Agentic Appliance Insights")

PROJECT = os.environ.get("GCP_PROJECT", "")
REGION = os.environ.get("GCP_REGION", "europe-west1")
DATASET = os.environ.get("BQ_DATASET", "")
TABLE = os.environ.get("BQ_TABLE", "")

_repository = BigQueryApplianceRepository(project=PROJECT, dataset=DATASET, table=TABLE)
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
