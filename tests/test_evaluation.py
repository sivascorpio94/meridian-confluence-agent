import unittest
from types import SimpleNamespace

from eval.run_rag_evaluation import contains_all, score_case
from src.bedrock_chat import ChatResult
from src.rag_context import EvidenceBundle
from src.rag_pipeline import RagTimings


class EvaluationTest(unittest.TestCase):
    def test_contains_all_is_case_insensitive(self):
        self.assertTrue(contains_all("Use ServiceNow and PCI training", ["servicenow", "pci"]))
        self.assertFalse(contains_all("Use ServiceNow", ["ServiceNow", "PCI"]))

    def test_scores_grounded_answer(self):
        def item(page_id, warnings=()):
            hit = SimpleNamespace(page_id=page_id)
            return SimpleNamespace(hit=hit, warnings=warnings)

        canonical = item("page-01")
        stale = item("page-02", ("page may be stale",))
        result = SimpleNamespace(
            ranked=(canonical, stale),
            evidence=EvidenceBundle((canonical,), (stale,)),
            answer=ChatResult(
                "Use ServiceNow with MOSAIC_UI_VIEWER [page-01].",
                "test-model", 10, 5, 1, "end_turn"
            ),
            timings=RagTimings(1, 1, 1, 3),
        )
        case = {
            "id": "mosaic",
            "category": "test",
            "question": "How?",
            "preferred_pages": ["page-01"],
            "relevant_pages": ["page-01"],
            "misleading_pages": ["page-02"],
            "required_answer_terms": ["ServiceNow", "MOSAIC_UI_VIEWER"],
            "required_citations": ["page-01"],
            "expected_warning_pages": ["page-02"],
        }
        scored = score_case(case, result)
        self.assertTrue(scored["passed"])
        self.assertTrue(all(scored["metrics"].values()))


if __name__ == "__main__":
    unittest.main()
