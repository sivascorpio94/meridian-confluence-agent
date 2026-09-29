"""Framework-neutral knowledge operations exposed through MCP."""

from __future__ import annotations

import re

from src.api_contract import result_payload, source_payload
from src.bedrock_embeddings import BedrockEmbeddingClient
from src.rag_context import build_evidence_bundle
from src.rag_pipeline import answer_question as run_rag
from src.reranking import rerank
from src.vector_store import connect, load_page_metadata, similarity_search


PAGE_ID_RE = re.compile(r"^(?:page-\d{2}|conf-\d+)$")


def _evidence_sources(items, source_type: str) -> list[dict]:
    """Map ranked hits to UI metadata plus the evidence an agent needs to answer."""
    sources = source_payload(items, source_type)
    first_hit_by_page = {}
    for item in items:
        first_hit_by_page.setdefault(item.hit.page_id, item.hit)
    for source in sources:
        hit = first_hit_by_page[source["page_id"]]
        source["section_path"] = list(hit.section_path)
        # Bound tool-result size while retaining enough procedural evidence.
        source["content_excerpt"] = hit.content[:1_500]
    return sources


def search_knowledge(query: str, *, region: str = "us-east-2", limit: int = 5,
                     minimum_similarity: float = 0.30, embedding_client=None,
                     connection_factory=connect, source_scope: str = "all") -> dict:
    """Retrieve and trust-rerank evidence without invoking the chat model."""
    query = query.strip()
    if len(query) < 3:
        raise ValueError("query must contain at least 3 characters")
    if not 1 <= limit <= 10:
        raise ValueError("limit must be between 1 and 10")

    embedding_client = embedding_client or BedrockEmbeddingClient(region=region)
    query_embedding = embedding_client.embed(query)
    connection = connection_factory()
    try:
        candidates = similarity_search(
            connection, query_embedding.vector, max(8, limit * 3), source_scope
        )
        metadata = load_page_metadata(connection, source_scope)
    finally:
        connection.close()

    max_similarity = max((hit.similarity for hit in candidates), default=0.0)
    if max_similarity < minimum_similarity:
        return {"status": "insufficient_evidence", "query": query,
                "max_semantic_score": round(max_similarity, 4),
                "minimum_similarity": minimum_similarity, "sources": []}

    ranked = rerank(query, candidates, metadata, limit=max(8, limit), max_chunks_per_page=2)
    bundle = build_evidence_bundle(ranked, recommended_limit=limit, conflict_limit=limit)
    sources = _evidence_sources(bundle.recommended, "recommended")
    sources.extend(_evidence_sources(bundle.conflicts, "conflict"))
    return {"status": "found", "query": query,
            "max_semantic_score": round(max_similarity, 4),
            "minimum_similarity": minimum_similarity, "sources": sources[: limit * 2]}


def answer_knowledge_question(question: str, *, region: str = "us-east-2",
                              retrieve: int = 8, source_scope: str = "all") -> dict:
    """Run the evaluated RAG pipeline and return its structured response."""
    return result_payload(question, run_rag(
        question, region=region, retrieve=retrieve, source_scope=source_scope
    ))


def get_page_details(page_id: str, *, connection_factory=connect) -> dict:
    """Read one page and all of its stored chunks from PostgreSQL."""
    page_id = page_id.strip().lower()
    if not PAGE_ID_RE.fullmatch(page_id):
        raise ValueError("page_id must use the format page-01 or conf-123456")
    connection = connection_factory()
    try:
        rows = connection.execute(
            """SELECT page_id, title, section_path, content, metadata
               FROM document_chunks WHERE page_id = %s ORDER BY chunk_id""",
            (page_id,),
        ).fetchall()
    finally:
        connection.close()
    if not rows:
        return {"status": "not_found", "page_id": page_id}
    return {"status": "found", "page_id": page_id, "title": rows[0][1],
            "metadata": rows[0][4],
            "chunks": [{"section_path": list(row[2]), "content": row[3]} for row in rows]}


def check_document_conflicts(query: str, *, region: str = "us-east-2",
                             source_scope: str = "all") -> dict:
    """Find retrieved pages carrying stale, superseded, draft, or review warnings."""
    result = search_knowledge(
        query, region=region, limit=5, source_scope=source_scope
    )
    conflicts = [s for s in result["sources"] if s["source_type"] == "conflict"]
    return {"status": result["status"], "query": result["query"],
            "conflict_count": len(conflicts), "conflicts": conflicts}
