import unittest
from types import SimpleNamespace

from src.api_contract import result_payload, source_payload
from src.bedrock_chat import ChatResult
from src.rag_context import EvidenceBundle
from src.rag_pipeline import RagDecision, RagTimings


def evidence(page_id, *, warning=False):
    hit = SimpleNamespace(
        page_id=page_id,
        title=f"Title {page_id}",
        metadata={
            "url": f"https://wiki.example/{page_id}",
            "status": "current",
            "authority_level": "canonical",
        },
    )
    return SimpleNamespace(
        hit=hit,
        semantic_score=0.75,
        final_score=0.9,
        reasons=("canonical",),
        warnings=("stale",) if warning else (),
    )


class ApiContractTests(unittest.TestCase):
    def test_sources_are_deduplicated_by_page(self):
        first = evidence("page-01")
        duplicate = evidence("page-01")
        self.assertEqual(1, len(source_payload((first, duplicate), "recommended")))

    def test_result_contains_grounded_citations_usage_and_timings(self):
        recommended = evidence("page-01")
        conflict = evidence("page-02", warning=True)
        result = SimpleNamespace(
            answer=ChatResult(
                "Use ServiceNow [page-01].", "test-model", 100, 10, 20, "end_turn"
            ),
            evidence=EvidenceBundle((recommended,), (conflict,)),
            timings=RagTimings(1, 2, 3, 6),
            decision=RagDecision(max_semantic_score=0.75),
        )
        payload = result_payload("How?", result)
        self.assertEqual(["page-01"], payload["citations"])
        self.assertEqual(110, payload["usage"]["input_tokens"] + payload["usage"]["output_tokens"])
        self.assertEqual(6, payload["timings_ms"]["total"])
        self.assertEqual(["recommended", "conflict"], [s["source_type"] for s in payload["sources"]])


if __name__ == "__main__":
    unittest.main()
