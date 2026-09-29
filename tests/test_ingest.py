import unittest
from pathlib import Path

from src.ingest import embedding_fingerprint, load_chunks


CHUNKS = Path("data/processed/chunks.jsonl")


class IngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chunks = load_chunks(CHUNKS)

    def test_generated_chunk_count(self):
        self.assertEqual(152, len(self.chunks))

    def test_fingerprint_is_stable(self):
        chunk = self.chunks[0]
        first = embedding_fingerprint(chunk, "model-a", 1024)
        second = embedding_fingerprint(chunk, "model-a", 1024)
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))

    def test_fingerprint_changes_with_embedding_input(self):
        chunk = dict(self.chunks[0])
        original = embedding_fingerprint(chunk, "model-a", 1024)
        chunk["embedding_text"] += " changed"
        self.assertNotEqual(original, embedding_fingerprint(chunk, "model-a", 1024))

    def test_fingerprint_changes_with_model_configuration(self):
        chunk = self.chunks[0]
        original = embedding_fingerprint(chunk, "model-a", 1024)
        self.assertNotEqual(original, embedding_fingerprint(chunk, "model-b", 1024))
        self.assertNotEqual(original, embedding_fingerprint(chunk, "model-a", 512))


if __name__ == "__main__":
    unittest.main()

