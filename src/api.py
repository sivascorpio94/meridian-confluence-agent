"""Stage 8 FastAPI adapter for the Meridian manual RAG pipeline."""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from src.api_contract import result_payload
from src.bedrock_chat import DEFAULT_CHAT_MODEL_ID
from src.mcp_agent import ReusableMcpAgentRunner
from src.rag_pipeline import answer_question
from src.vector_store import connect


LOGGER = logging.getLogger("meridian.api")
DEFAULT_REGION = os.getenv("AWS_REGION", "us-east-2")
DEFAULT_MODEL = os.getenv("BEDROCK_CHAT_MODEL_ID", DEFAULT_CHAT_MODEL_ID)
MINIMUM_SIMILARITY = float(os.getenv("RAG_MINIMUM_SIMILARITY", "0.30"))
RAG_SOURCE_SCOPE = os.getenv("RAG_SOURCE_SCOPE", "confluence_cloud")
AGENT_TIMEOUT_SECONDS = float(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))
CORS_ORIGINS = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
).split(",") if origin.strip()]


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=3, max_length=2_000)
    retrieve: int = Field(default=8, ge=1, le=20)
    max_tokens: int = Field(default=250, ge=50, le=700)
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)


class SourceResponse(BaseModel):
    page_id: str
    title: str
    url: str | None
    status: str
    authority: str | None
    source_type: Literal["recommended", "conflict"]
    semantic_score: float
    final_score: float
    reasons: list[str]
    warnings: list[str]


class UsageResponse(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str


class TimingsResponse(BaseModel):
    embedding: int
    retrieval: int
    generation: int
    total: int


class ConfidenceResponse(BaseModel):
    max_semantic_score: float
    minimum_similarity: float
    reason: str


class AskResponse(BaseModel):
    question: str
    status: Literal["answered", "insufficient_evidence"]
    answer: str
    citations: list[str]
    sources: list[SourceResponse]
    validation_warnings: list[str]
    confidence: ConfidenceResponse
    usage: UsageResponse
    timings_ms: TimingsResponse


class AgentAskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=3, max_length=2_000)
    max_steps: int = Field(default=4, ge=1, le=10)
    max_tokens: int = Field(default=500, ge=50, le=1_000)


class AgentToolCallResponse(BaseModel):
    step: int
    tool: str
    arguments: dict
    status: Literal["success", "error"]
    duplicate: bool
    duration_ms: int


class AgentUsageResponse(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class AgentTimingResponse(BaseModel):
    mcp_startup: int = 0
    model: int = 0
    tools: int = 0
    total: int


class AgentAskResponse(BaseModel):
    question: str
    status: Literal["answered", "safety_limit"]
    answer: str
    citations: list[str]
    sources: list[dict]
    tool_calls: list[AgentToolCallResponse]
    usage: AgentUsageResponse
    timings_ms: AgentTimingResponse


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        runner = application.state.agent_runner
        start = getattr(runner, "start", None)
        if start is not None:
            await start()
        try:
            yield
        finally:
            close = getattr(runner, "close", None)
            if close is not None:
                await close()

    app = FastAPI(
        title="Meridian Confluence Agent API",
        description="Trust-aware RAG over a fictional enterprise knowledge base.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )
    app.state.rag_runner = answer_question
    app.state.agent_runner = ReusableMcpAgentRunner(
        region=DEFAULT_REGION,
        model_id=DEFAULT_MODEL,
    )
    app.state.connection_factory = connect

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request: Request, exc: RuntimeError):
        LOGGER.exception("RAG dependency failed path=%s", request.url.path)
        return JSONResponse(
            status_code=503,
            content={"detail": "A required RAG dependency is unavailable."},
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        LOGGER.exception("Unexpected API failure path=%s", request.url.path)
        return JSONResponse(
            status_code=502,
            content={"detail": "The answer service could not complete the request."},
        )

    @app.get("/health", tags=["operations"])
    async def health() -> dict:
        return {"status": "ok", "service": "meridian-confluence-agent"}

    @app.get("/ready", tags=["operations"])
    async def ready() -> dict:
        def check_database() -> None:
            connection = app.state.connection_factory()
            try:
                connection.execute("SELECT 1").fetchone()
            finally:
                connection.close()

        await run_in_threadpool(check_database)
        runner = app.state.agent_runner
        mcp_status = "connected" if getattr(runner, "started", True) else "unavailable"
        return {"status": "ready", "database": "available", "mcp": mcp_status}

    @app.post("/ask", response_model=AskResponse, tags=["rag"])
    async def ask(body: AskRequest) -> dict:
        # boto3 and psycopg are synchronous, so keep them off the event loop.
        result = await run_in_threadpool(
            app.state.rag_runner,
            body.question,
            region=DEFAULT_REGION,
            model_id=DEFAULT_MODEL,
            retrieve=body.retrieve,
            max_tokens=body.max_tokens,
            temperature=body.temperature,
            minimum_similarity=MINIMUM_SIMILARITY,
            source_scope=RAG_SOURCE_SCOPE,
        )
        return result_payload(body.question, result)

    @app.post("/agent/ask", response_model=AgentAskResponse, tags=["agent"])
    async def agent_ask(body: AgentAskRequest) -> dict:
        try:
            async with asyncio.timeout(AGENT_TIMEOUT_SECONDS):
                return await app.state.agent_runner(
                    body.question,
                    region=DEFAULT_REGION,
                    model_id=DEFAULT_MODEL,
                    max_steps=body.max_steps,
                    max_tokens=body.max_tokens,
                )
        except TimeoutError as exc:
            LOGGER.warning("Agent request timed out after %.1fs", AGENT_TIMEOUT_SECONDS)
            raise HTTPException(
                status_code=504,
                detail="The agent exceeded its response-time limit. Please try again.",
            ) from exc

    return app


app = create_app()
