"""Reusable, observable manual RAG pipeline shared by the CLI and evaluator."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from src.bedrock_chat import BedrockChatClient, ChatResult, DEFAULT_CHAT_MODEL_ID
from src.bedrock_embeddings import BedrockEmbeddingClient
from src.rag_context import EvidenceBundle, SYSTEM_PROMPT, build_evidence_bundle, build_user_prompt
from src.reranking import RerankedHit, rerank
from src.vector_store import connect, load_page_metadata, similarity_search


@dataclass(frozen=True)
class RagTimings:
    embedding_ms: int
    retrieval_ms: int
    generation_ms: int
    total_ms: int


@dataclass(frozen=True)
class RagDecision:
    status: str = "answered"
    reason: str = "sufficient_evidence"
    max_semantic_score: float = 0.0
    minimum_similarity: float = 0.30


@dataclass(frozen=True)
class RagResult:
    answer: ChatResult
    ranked: tuple[RerankedHit, ...]
    evidence: EvidenceBundle
    user_prompt: str
    timings: RagTimings
    decision: RagDecision = field(default_factory=RagDecision)


def answer_question(
    question: str,
    *,
    region: str = "us-east-2",
    model_id: str = DEFAULT_CHAT_MODEL_ID,
    retrieve: int = 8,
    temperature: float = 0.1,
    max_tokens: int = 250,
    minimum_similarity: float = 0.30,
    source_scope: str = "all",
    progress: Callable[[str], None] | None = None,
    embedding_client=None,
    chat_client=None,
    connection_factory=connect,
    similarity_search_fn=similarity_search,
    load_metadata_fn=load_page_metadata,
) -> RagResult:
    """Run all RAG stages while exposing evidence and per-stage latency."""
    report = progress or (lambda _message: None)
    total_started = time.perf_counter()

    report("Embedding question...")
    started = time.perf_counter()
    embedding_client = embedding_client or BedrockEmbeddingClient(region=region)
    query_result = embedding_client.embed(question)
    embedding_ms = int((time.perf_counter() - started) * 1_000)

    report("Retrieving and reranking evidence...")
    started = time.perf_counter()
    connection = connection_factory()
    try:
        candidates = similarity_search_fn(
            connection, query_result.vector, retrieve, source_scope
        )
        metadata = load_metadata_fn(connection, source_scope)
    finally:
        connection.close()
    ranked = rerank(question, candidates, metadata, limit=retrieve, max_chunks_per_page=2)
    evidence = build_evidence_bundle(ranked)
    user_prompt = build_user_prompt(question, evidence)
    retrieval_ms = int((time.perf_counter() - started) * 1_000)

    max_semantic_score = max((hit.similarity for hit in candidates), default=0.0)
    if max_semantic_score < minimum_similarity:
        report("Stopping: retrieved evidence is below the confidence threshold.")
        total_ms = int((time.perf_counter() - total_started) * 1_000)
        return RagResult(
            answer=ChatResult(
                text=(
                    "I couldn't find sufficiently relevant Meridian documentation "
                    "to answer that question. Try including the platform name and "
                    "the access or process you need."
                ),
                model_id="not-invoked",
                input_tokens=0,
                output_tokens=0,
                latency_ms=0,
                stop_reason="insufficient_evidence",
            ),
            ranked=tuple(ranked),
            evidence=EvidenceBundle((), ()),
            user_prompt="",
            timings=RagTimings(embedding_ms, retrieval_ms, 0, total_ms),
            decision=RagDecision(
                status="insufficient_evidence",
                reason="max_semantic_score_below_threshold",
                max_semantic_score=max_semantic_score,
                minimum_similarity=minimum_similarity,
            ),
        )

    report("Generating grounded answer...")
    started = time.perf_counter()
    chat_client = chat_client or BedrockChatClient(region=region, model_id=model_id)
    answer = chat_client.generate(
        SYSTEM_PROMPT,
        user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    generation_ms = int((time.perf_counter() - started) * 1_000)
    total_ms = int((time.perf_counter() - total_started) * 1_000)

    return RagResult(
        answer=answer,
        ranked=tuple(ranked),
        evidence=evidence,
        user_prompt=user_prompt,
        timings=RagTimings(embedding_ms, retrieval_ms, generation_ms, total_ms),
        decision=RagDecision(
            max_semantic_score=max_semantic_score,
            minimum_similarity=minimum_similarity,
        ),
    )
