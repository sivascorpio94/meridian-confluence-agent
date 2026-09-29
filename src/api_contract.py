"""Framework-neutral response mapping for the HTTP API."""

from __future__ import annotations

from src.rag_context import CITATION_RE, citation_warnings


def source_payload(items, source_type: str) -> list[dict]:
    """Return one explainable source entry per page, preserving rank order."""
    sources: list[dict] = []
    seen: set[str] = set()
    for item in items:
        hit = item.hit
        if hit.page_id in seen:
            continue
        seen.add(hit.page_id)
        sources.append(
            {
                "page_id": hit.page_id,
                "title": hit.title,
                "url": hit.metadata.get("url"),
                "status": hit.metadata.get("status", "unknown"),
                "authority": hit.metadata.get("authority_level"),
                "source_type": source_type,
                "semantic_score": round(item.semantic_score, 4),
                "final_score": round(item.final_score, 4),
                "reasons": list(item.reasons),
                "warnings": list(item.warnings),
            }
        )
    return sources


def result_payload(question: str, result) -> dict:
    citations = sorted(set(CITATION_RE.findall(result.answer.text)))
    validation_warnings = (
        list(citation_warnings(result.answer.text, result.evidence.page_ids))
        if result.decision.status == "answered"
        else []
    )
    return {
        "question": question,
        "status": result.decision.status,
        "answer": result.answer.text,
        "citations": citations,
        "sources": source_payload(result.evidence.recommended, "recommended")
        + source_payload(result.evidence.conflicts, "conflict"),
        "validation_warnings": validation_warnings,
        "confidence": {
            "max_semantic_score": round(result.decision.max_semantic_score, 4),
            "minimum_similarity": result.decision.minimum_similarity,
            "reason": result.decision.reason,
        },
        "usage": {
            "model": result.answer.model_id,
            "input_tokens": result.answer.input_tokens,
            "output_tokens": result.answer.output_tokens,
            "stop_reason": result.answer.stop_reason,
        },
        "timings_ms": {
            "embedding": result.timings.embedding_ms,
            "retrieval": result.timings.retrieval_ms,
            "generation": result.timings.generation_ms,
            "total": result.timings.total_ms,
        },
    }
