import unittest
from datetime import date
from pathlib import Path

from src.baseline_search import load_corpus
from src.reranking import rerank, score_metadata, superseded_page_ids
from src.vector_store import SearchHit


PAGES = {page.page_id: page for page in load_corpus(Path("data/raw_pages"))}
AS_OF = date(2026, 9, 15)


def hit(page_id: str, similarity: float, section: str = "Test") -> SearchHit:
    page = PAGES[page_id]
    return SearchHit(
        chunk_id=f"{page_id}::test::001",
        page_id=page_id,
        title=page.title,
        section_path=(page.title, section),
        content=page.body,
        metadata=page.metadata,
        similarity=similarity,
    )


class RerankingTests(unittest.TestCase):
    def test_supersedes_relationship_marks_old_page(self):
        ids = superseded_page_ids(page.metadata for page in PAGES.values())
        self.assertIn("page-02", ids)
        self.assertNotIn("page-01", ids)

    def test_canonical_procedure_beats_more_similar_stale_pages(self):
        candidates = [hit("page-02", 0.7250), hit("page-22", 0.7134), hit("page-01", 0.5551)]
        results = rerank(
            "How do I obtain read-only access to Mosaic?",
            candidates,
            [page.metadata for page in PAGES.values()],
            as_of=AS_OF,
        )
        self.assertEqual("page-01", results[0].hit.page_id)
        stale = next(item for item in results if item.hit.page_id == "page-02")
        self.assertIn("page is superseded", stale.warnings)

    def test_under_review_faq_remains_visible_with_warning(self):
        results = rerank(
            "How do I get Mosaic access?",
            [hit("page-22", 0.71)],
            [page.metadata for page in PAGES.values()],
            as_of=AS_OF,
        )
        self.assertEqual(1, len(results))
        self.assertIn("document status is under_review", results[0].warnings)

    def test_confluence_lifecycle_label_marks_page_superseded(self):
        metadata = {
            "id": "conf-100",
            "status": "current",
            "lifecycle": "superseded",
        }
        self.assertIn("conf-100", superseded_page_ids([metadata]))

    def test_confluence_timestamp_is_used_for_staleness(self):
        base = hit("page-01", 0.60)
        timestamped = SearchHit(**{
            **base.__dict__,
            "page_id": "conf-100",
            "metadata": {
                "status": "current",
                "last_updated": "2023-01-10T12:30:00Z",
            },
        })
        _, reasons, warnings = score_metadata(
            "Mosaic reference", timestamped, set(), as_of=AS_OF
        )
        self.assertIn("last updated over 2 years ago (-0.10)", reasons)
        self.assertIn("page may be stale", warnings)

    def test_audit_is_not_penalized_for_audit_query(self):
        audit = hit("page-23", 0.70)
        procedural_adjustment, _, _ = score_metadata(
            "How do I request PaySure access?", audit, set(), as_of=AS_OF
        )
        audit_adjustment, _, _ = score_metadata(
            "Show me the Q3 access audit report", audit, set(), as_of=AS_OF
        )
        self.assertGreater(audit_adjustment, procedural_adjustment)

    def test_diversity_caps_chunks_per_page(self):
        candidates = [
            hit("page-01", 0.90, "A"),
            SearchHit(**{**hit("page-01", 0.89, "B").__dict__, "chunk_id": "page-01::b::002"}),
            SearchHit(**{**hit("page-01", 0.88, "C").__dict__, "chunk_id": "page-01::c::003"}),
            hit("page-03", 0.60),
        ]
        results = rerank(
            "Mosaic role reference",
            candidates,
            [page.metadata for page in PAGES.values()],
            limit=4,
            max_chunks_per_page=2,
            as_of=AS_OF,
        )
        self.assertEqual(2, sum(item.hit.page_id == "page-01" for item in results))


if __name__ == "__main__":
    unittest.main()
