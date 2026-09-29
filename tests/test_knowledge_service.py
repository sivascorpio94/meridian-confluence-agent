import unittest
from types import SimpleNamespace

from src.knowledge_service import _evidence_sources, get_page_details


class FakeResult:
    def fetchall(self):
        return [("page-01", "Mosaic UI Access Request Procedure",
                 ["Mosaic UI", "Roles"], "MOSAIC_UI_VIEWER is read-only.",
                 {"page_id": "page-01", "status": "current"})]


class FakeConnection:
    def __init__(self): self.closed = False
    def execute(self, statement, parameters): return FakeResult()
    def close(self): self.closed = True


class KnowledgeServiceTests(unittest.TestCase):
    def test_evidence_sources_include_bounded_content(self):
        hit = SimpleNamespace(
            page_id="page-01", title="Procedure", section_path=("Access", "Steps"),
            content="Open ServiceNow. " * 200,
            metadata={"status": "current", "authority_level": "canonical"},
        )
        item = SimpleNamespace(
            hit=hit, semantic_score=0.7, final_score=0.9,
            reasons=(), warnings=(),
        )
        source = _evidence_sources([item], "recommended")[0]
        self.assertEqual(["Access", "Steps"], source["section_path"])
        self.assertLessEqual(len(source["content_excerpt"]), 1500)
        self.assertIn("Open ServiceNow", source["content_excerpt"])

    def test_page_id_is_validated(self):
        with self.assertRaises(ValueError):
            get_page_details("../../secrets")

    def test_page_details_are_structured(self):
        connection = FakeConnection()
        result = get_page_details("PAGE-01", connection_factory=lambda: connection)
        self.assertEqual("found", result["status"])
        self.assertEqual("page-01", result["page_id"])
        self.assertEqual(1, len(result["chunks"]))
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
