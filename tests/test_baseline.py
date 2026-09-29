import unittest
from pathlib import Path

from src.baseline_search import BM25Search, load_corpus, tokenize


ROOT = Path(__file__).resolve().parents[1]


class BaselineSearchTest(unittest.TestCase):
    def test_tokenize_preserves_role_names(self) -> None:
        self.assertIn("mosaic_ui_viewer", tokenize("Request MOSAIC_UI_VIEWER access"))

    def test_loads_frozen_corpus(self) -> None:
        pages = load_corpus(ROOT / "data/raw_pages")
        self.assertEqual(25, len(pages))
        self.assertEqual(25, len({page.page_id for page in pages}))

    def test_mosaic_query_retrieves_a_relevant_page(self) -> None:
        engine = BM25Search(load_corpus(ROOT / "data/raw_pages"))
        ids = [page.page_id for page, _ in engine.search("read-only Mosaic UI access", 5)]
        self.assertTrue("page-01" in ids or "page-03" in ids)


if __name__ == "__main__":
    unittest.main()
