import unittest

from src.vector_store import _source_clause


class VectorStoreSourceTests(unittest.TestCase):
    def test_all_scope_has_no_filter(self):
        self.assertEqual(("", ()), _source_clause("all"))

    def test_confluence_scope_uses_explicit_source_metadata(self):
        clause, parameters = _source_clause("confluence_cloud")
        self.assertIn("metadata->>'source'", clause)
        self.assertEqual(("confluence_cloud",), parameters)

    def test_frozen_scope_includes_legacy_rows_without_source_metadata(self):
        clause, parameters = _source_clause("frozen_corpus")
        self.assertIn("COALESCE", clause)
        self.assertEqual(("frozen_corpus",), parameters)

    def test_unknown_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            _source_clause("everything")


if __name__ == "__main__":
    unittest.main()
