from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .graph import build_graph
from .planner import OpenAIPlanner, PlannerConfigurationError
from .retrieval import render_answer, retrieve


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class QueryResponse(BaseModel):
    planner: str
    plan: dict[str, Any]
    answer: str
    records: list[dict[str, Any]]
    
app = FastAPI(
    title="Commerce Knowledge Graph API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

load_dotenv()
graph = build_graph()
planner = OpenAIPlanner()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        plan = planner.plan(request.question)
        records = retrieve(graph, plan)
    except PlannerConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Could not plan or retrieve the graph query.",
        ) from error

    return QueryResponse(
        planner="OpenAI",
        plan=plan,
        answer=render_answer(records),
        records=records,
    )