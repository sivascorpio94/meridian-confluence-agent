import asyncio
import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient

import src.api as api_module
from src.api import create_app
from src.bedrock_chat import ChatResult
from src.rag_context import EvidenceBundle
from src.rag_pipeline import RagDecision, RagResult, RagTimings


def reranked(page_id: str, *, warnings=()):
    hit = SimpleNamespace(
        page_id=page_id,
        title="Mosaic UI Access Request Procedure",
        metadata={
            "url": f"https://wiki.example/{page_id}",
            "status": "current",
            "authority_level": "canonical",
        },
    )
    return SimpleNamespace(
        hit=hit,
        semantic_score=0.75,
        final_score=0.95,
        reasons=("authority=canonical",),
        warnings=tuple(warnings),
    )


def fake_result() -> RagResult:
    recommended = reranked("page-01")
    conflict = reranked("page-02", warnings=("page may be stale",))
    return RagResult(
        answer=ChatResult(
            "Use ServiceNow [page-01].", "test-model", 100, 10, 20, "end_turn"
        ),
        ranked=(recommended, conflict),
        evidence=EvidenceBundle((recommended,), (conflict,)),
        user_prompt="prompt",
        timings=RagTimings(1, 2, 3, 6),
    )


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.state.rag_runner = lambda question, **kwargs: fake_result()
        async def fake_agent_runner(question, **kwargs):
            return {
                "question": question,
                "status": "answered",
                "answer": "Use ServiceNow [page-01].",
                "citations": ["page-01"],
                "sources": [{"page_id": "page-01", "title": "Mosaic Procedure"}],
                "tool_calls": [{
                    "step": 1, "tool": "search_knowledge",
                    "arguments": {"query": "Mosaic access"},
                    "status": "success", "duplicate": False, "duration_ms": 25,
                }],
                "usage": {"model": "test-model", "input_tokens": 100,
                          "output_tokens": 20, "total_tokens": 120},
                "timings_ms": {"total": 50},
            }
        self.app.state.agent_runner = fake_agent_runner
        self.client = TestClient(self.app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])
        self.assertTrue(response.headers.get("X-Request-ID"))

    def test_ask_returns_structured_grounded_response(self):
        response = self.client.post("/ask", json={"question": "How do I get access?"})
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual(["page-01"], body["citations"])
        self.assertEqual(2, len(body["sources"]))
        self.assertEqual("recommended", body["sources"][0]["source_type"])
        self.assertEqual(6, body["timings_ms"]["total"])

    def test_ask_rejects_unknown_fields(self):
        response = self.client.post(
            "/ask", json={"question": "How do I get access?", "debug": True}
        )
        self.assertEqual(422, response.status_code)

    def test_ask_rejects_out_of_range_configuration(self):
        response = self.client.post(
            "/ask", json={"question": "How do I get access?", "retrieve": 100}
        )
        self.assertEqual(422, response.status_code)

    def test_agent_ask_returns_tool_trace(self):
        response = self.client.post(
            "/agent/ask", json={"question": "How do I get access?"}
        )
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("search_knowledge", body["tool_calls"][0]["tool"])
        self.assertEqual(["page-01"], body["citations"])
        self.assertEqual(120, body["usage"]["total_tokens"])

    def test_agent_ask_rejects_invalid_step_limit(self):
        response = self.client.post(
            "/agent/ask", json={"question": "How do I get access?", "max_steps": 99}
        )
        self.assertEqual(422, response.status_code)

    def test_agent_timeout_returns_504(self):
        async def slow_agent_runner(question, **kwargs):
            await asyncio.sleep(0.05)

        original_timeout = api_module.AGENT_TIMEOUT_SECONDS
        self.app.state.agent_runner = slow_agent_runner
        api_module.AGENT_TIMEOUT_SECONDS = 0.001
        try:
            response = self.client.post(
                "/agent/ask", json={"question": "How do I get access?"}
            )
        finally:
            api_module.AGENT_TIMEOUT_SECONDS = original_timeout

        self.assertEqual(504, response.status_code)
        self.assertIn("response-time limit", response.json()["detail"])

    def test_low_confidence_response_has_no_sources_or_generation_usage(self):
        self.app.state.rag_runner = lambda question, **kwargs: RagResult(
            answer=ChatResult(
                "I couldn't find sufficiently relevant Meridian documentation.",
                "not-invoked", 0, 0, 0, "insufficient_evidence"
            ),
            ranked=(),
            evidence=EvidenceBundle((), ()),
            user_prompt="",
            timings=RagTimings(10, 2, 0, 12),
            decision=RagDecision(
                "insufficient_evidence",
                "max_semantic_score_below_threshold",
                0.1165,
                0.30,
            ),
        )
        response = self.client.post("/ask", json={"question": "string"})
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("insufficient_evidence", body["status"])
        self.assertEqual([], body["sources"])
        self.assertEqual([], body["citations"])
        self.assertEqual(0, body["usage"]["input_tokens"])


if __name__ == "__main__":
    unittest.main()
