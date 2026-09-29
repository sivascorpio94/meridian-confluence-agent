import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.rag_pipeline import answer_question
from src.vector_store import SearchHit


class Connection:
    def close(self):
        pass


class ConfidenceGateTests(unittest.TestCase):
    def test_low_similarity_stops_before_chat_generation(self):
        embedding_client = Mock()
        embedding_client.embed.return_value = SimpleNamespace(vector=(0.1, 0.2))
        chat_client = Mock()
        candidates = [
            SearchHit(
                chunk_id="page-25-overview-001",
                page_id="page-25",
                title="Glossary",
                section_path=("Glossary",),
                content="Terms",
                metadata={"page_id": "page-25", "status": "current"},
                similarity=0.1165,
            )
        ]

        result = answer_question(
            "string",
            embedding_client=embedding_client,
            chat_client=chat_client,
            connection_factory=Connection,
            similarity_search_fn=lambda connection, vector, limit, source: candidates,
            load_metadata_fn=lambda connection, source: [candidates[0].metadata],
        )

        self.assertEqual("insufficient_evidence", result.decision.status)
        self.assertEqual("not-invoked", result.answer.model_id)
        self.assertEqual(0, result.timings.generation_ms)
        self.assertEqual((), result.evidence.recommended)
        chat_client.generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
