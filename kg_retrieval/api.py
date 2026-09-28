import logging
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .graph import build_graph
from .logging_config import configure_logging
from .planner import (
    GroqPlanner,
    PlannerConfigurationError,
    PlannerModelError,
    PlannerUnavailableError,
)
from .retrieval import render_answer, retrieve

configure_logging()
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class QueryResponse(BaseModel):
    planner: str
    plan: dict[str, Any]
    answer: str
    records: list[dict[str, Any]]
    
app = FastAPI(
    title="Commerce Knowledge Graph API",
)

load_dotenv()
graph = build_graph()
planner = GroqPlanner()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    logger.info("Query received (question_length=%d)", len(request.question))
    try:
        logger.info("Planning query with Groq")
        plan = planner.plan(request.question)
        logger.info("Query plan created (filters=%s)", sorted(plan["filters"]))

        logger.info("Retrieving matching records from graph")
        records = retrieve(graph, plan)
        logger.info("Graph retrieval completed (record_count=%d)", len(records))
    except PlannerConfigurationError as error:
        logger.warning("Query unavailable because Groq is not configured: %s", error)
        raise HTTPException(status_code=503, detail=str(error)) from error
    except PlannerModelError as error:
        logger.error("Configured Groq model is unavailable: %s", error)
        raise HTTPException(status_code=503, detail=str(error)) from error
    except PlannerUnavailableError as error:
        logger.warning("Groq is temporarily unavailable: %s", error)
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Query processing failed")
        raise HTTPException(
            status_code=502,
            detail="Could not plan or retrieve the graph query.",
        ) from error

    logger.info("Formatting grounded answer")
    answer = render_answer(records)
    logger.info("Query completed successfully")
    return QueryResponse(
        planner="Groq",
        plan=plan,
        answer=answer,
        records=records,
    )