"""Explainable metadata-aware reranking layered on semantic retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping

from src.vector_store import SearchHit


PROCEDURAL_TERMS = {
    "how", "request", "obtain", "access", "setup", "configure", "steps", "need"
}
AUDIT_TERMS = {"audit", "report", "finding", "findings", "quarter", "q1", "q2", "q3", "q4"}


@dataclass(frozen=True)
class RerankedHit:
    hit: SearchHit
    semantic_score: float
    metadata_adjustment: float
    final_score: float
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


def superseded_page_ids(page_metadata: Iterable[Mapping]) -> set[str]:
    """Resolve both outgoing `supersedes` links and incoming replacement links."""
    superseded: set[str] = set()
    for metadata in page_metadata:
        superseded.update(metadata.get("supersedes") or [])
        if metadata.get("superseded_by") or metadata.get("lifecycle") == "superseded":
            page_id = metadata.get("page_id") or metadata.get("id")
            if page_id:
                superseded.add(page_id)
    return superseded


def _is_procedural(query: str) -> bool:
    words = {word.strip("?!.,:").lower() for word in query.split()}
    return bool(words & PROCEDURAL_TERMS) and not bool(words & AUDIT_TERMS)


def _parse_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        # Confluence returns RFC 3339 timestamps; trust scoring needs only the date.
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def score_metadata(
    query: str,
    hit: SearchHit,
    superseded_ids: set[str],
    as_of: date | None = None,
) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    """Return a bounded adjustment and its human-readable evidence."""
    as_of = as_of or date.today()
    metadata = hit.metadata
    adjustment = 0.0
    reasons: list[str] = []
    warnings: list[str] = []

    status = metadata.get("status")
    status_weights = {
        "current": 0.06,
        "under_review": -0.12,
        "draft": -0.25,
        "deprecated": -0.40,
    }
    if status in status_weights:
        value = status_weights[status]
        adjustment += value
        reasons.append(f"status={status} ({value:+.2f})")
        if status != "current":
            warnings.append(f"document status is {status}")

    authority = metadata.get("authority_level")
    authority_weights = {
        "canonical": 0.14,
        "standard": 0.06,
        "draft-only": -0.20,
        "deprecated": -0.35,
    }
    if authority in authority_weights:
        value = authority_weights[authority]
        adjustment += value
        reasons.append(f"authority={authority} ({value:+.2f})")
    elif authority is None:
        reasons.append("authority=absent (+0.00)")

    if hit.page_id in superseded_ids:
        adjustment -= 0.35
        reasons.append("superseded by another page (-0.35)")
        warnings.append("page is superseded")

    document_type = metadata.get("document_type")
    if _is_procedural(query):
        type_weights = {
            "procedure": 0.05,
            "checklist": 0.03,
            "faq": -0.03,
            "audit": -0.12,
            "glossary": -0.05,
        }
        if document_type in type_weights:
            value = type_weights[document_type]
            adjustment += value
            reasons.append(f"procedural intent + type={document_type} ({value:+.2f})")

    updated = _parse_date(metadata.get("last_updated"))
    if updated:
        age_days = (as_of - updated).days
        if age_days > 730:
            adjustment -= 0.10
            reasons.append("last updated over 2 years ago (-0.10)")
            warnings.append("page may be stale")
        elif age_days > 365:
            adjustment -= 0.04
            reasons.append("last updated over 1 year ago (-0.04)")

    # Keep metadata from overwhelming semantic relevance completely.
    adjustment = max(-0.60, min(0.30, adjustment))
    return adjustment, tuple(reasons), tuple(warnings)


def rerank(
    query: str,
    hits: Iterable[SearchHit],
    page_metadata: Iterable[Mapping],
    limit: int = 5,
    max_chunks_per_page: int = 2,
    as_of: date | None = None,
) -> list[RerankedHit]:
    superseded_ids = superseded_page_ids(page_metadata)
    scored: list[RerankedHit] = []
    for hit in hits:
        adjustment, reasons, warnings = score_metadata(
            query, hit, superseded_ids, as_of=as_of
        )
        scored.append(
            RerankedHit(
                hit=hit,
                semantic_score=hit.similarity,
                metadata_adjustment=adjustment,
                final_score=hit.similarity + adjustment,
                reasons=reasons,
                warnings=warnings,
            )
        )

    scored.sort(key=lambda item: (-item.final_score, -item.semantic_score, item.hit.chunk_id))
    selected: list[RerankedHit] = []
    page_counts: dict[str, int] = {}
    for item in scored:
        count = page_counts.get(item.hit.page_id, 0)
        if count >= max_chunks_per_page:
            continue
        selected.append(item)
        page_counts[item.hit.page_id] = count + 1
        if len(selected) == limit:
            break
    return selected
