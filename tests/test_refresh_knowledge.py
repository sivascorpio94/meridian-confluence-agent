import unittest
from types import SimpleNamespace

from src.refresh_knowledge import is_governed


class RefreshKnowledgeTests(unittest.TestCase):
    def test_governed_page_is_selected(self):
        page = SimpleNamespace(metadata={"labels": ["status-current", "type-procedure"]})
        self.assertTrue(is_governed(page))

    def test_unlabeled_template_is_excluded(self):
        page = SimpleNamespace(metadata={"labels": []})
        self.assertFalse(is_governed(page))


if __name__ == "__main__":
    unittest.main()
