import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.baseline_search import load_corpus
from src.chunking import chunk_corpus, chunk_page, write_jsonl


CORPUS = Path("data/raw_pages")


class ChunkingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = load_corpus(CORPUS)
        cls.chunks = chunk_corpus(cls.pages)

    def test_all_pages_produce_chunks_with_unique_ids(self):
        self.assertEqual(25, len({chunk.page_id for chunk in self.chunks}))
        self.assertEqual(len(self.chunks), len({chunk.chunk_id for chunk in self.chunks}))

    def test_chunks_are_bounded_and_have_embedding_context(self):
        for chunk in self.chunks:
            self.assertTrue(chunk.text.strip())
            self.assertLessEqual(len(chunk.embedding_text), 1_400)
            self.assertTrue(chunk.embedding_text.startswith(f"Page: {chunk.title}\n"))
            self.assertIn("\nSection: ", chunk.embedding_text)

    def test_retrieval_metadata_is_preserved(self):
        mosaic = next(chunk for chunk in self.chunks if chunk.page_id == "page-01")
        self.assertEqual("current", mosaic.metadata["status"])
        self.assertEqual("canonical", mosaic.metadata["authority_level"])
        self.assertEqual("2026-07-15", mosaic.metadata["last_updated"])
        self.assertEqual("page-01.md", mosaic.metadata["source_file"])

    def test_missing_authority_is_not_invented(self):
        page_20 = next(page for page in self.pages if page.page_id == "page-20")
        for chunk in chunk_page(page_20):
            self.assertNotIn("authority_level", chunk.metadata)

    def test_section_path_is_attached(self):
        roles = next(
            chunk
            for chunk in self.chunks
            if chunk.page_id == "page-01" and chunk.section_path[-1] == "Roles"
        )
        self.assertEqual(("Mosaic UI Access Request Procedure", "Roles"), roles.section_path)
        self.assertIn("MOSAIC_UI_VIEWER", roles.text)

    def test_jsonl_round_trip(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "chunks.jsonl"
            count = write_jsonl(self.chunks, output)
            records = [json.loads(line) for line in output.read_text().splitlines()]
        self.assertEqual(len(self.chunks), count)
        self.assertEqual(len(self.chunks), len(records))
        self.assertIn("embedding_text", records[0])

    def test_invalid_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            chunk_page(self.pages[0], max_chars=500, overlap_chars=500)


if __name__ == "__main__":
    unittest.main()
