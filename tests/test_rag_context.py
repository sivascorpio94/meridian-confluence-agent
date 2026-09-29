import unittest
from datetime import date
from pathlib import Path

from src.baseline_search import load_corpus
from src.rag_context import build_evidence_bundle, build_user_prompt, citation_warnings
from src.reranking import rerank
from src.vector_store import SearchHit


PAGES = {page.page_id: page for page in load_corpus(Path("data/raw_pages"))}


def hit(page_id: str, similarity: float) -> SearchHit:
    page = PAGES[page_id]
    return SearchHit(
        chunk_id=f"{page_id}::test::001",
        page_id=page_id,
        title=page.title,
        section_path=(page.title, "Test"),
        content=page.body[:500],
        metadata=page.metadata,
        similarity=similarity,
    )


class RagContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = rerank(
            "How do I obtain read-only Mosaic access?",
            [hit("page-02", 0.725), hit("page-22", 0.7134), hit("page-01", 0.5551)],
            [page.metadata for page in PAGES.values()],
            limit=3,
            as_of=date(2026, 9, 15),
        )
        cls.bundle = build_evidence_bundle(cls.results)

    def test_recommended_and_conflicting_evidence_are_separated(self):
        self.assertEqual(["page-01"], [item.hit.page_id for item in self.bundle.recommended])
        self.assertEqual(
            {"page-02", "page-22"},
            {item.hit.page_id for item in self.bundle.conflicts},
        )

    def test_prompt_contains_provenance_and_separate_lanes(self):
        prompt = build_user_prompt("How do I get access?", self.bundle)
        self.assertIn("RECOMMENDED EVIDENCE", prompt)
        self.assertIn("CONFLICTING OR STALE EVIDENCE", prompt)
        self.assertIn("SOURCE [page-01]", prompt)
        self.assertIn("SOURCE [page-02]", prompt)
        self.assertIn("URL:", prompt)

    def test_citation_validation(self):
        self.assertEqual((), citation_warnings("Use ServiceNow [page-01].", {"page-01"}))
        self.assertEqual((), citation_warnings("Use the guide [conf-123456].", {"conf-123456"}))
        self.assertIn("answer contains no page citations", citation_warnings("No citation", {"page-01"}))
        self.assertIn(
            "answer cites unknown pages: page-99",
            citation_warnings("Claim [page-99]", {"page-01"}),
        )


if __name__ == "__main__":
    unittest.main()
