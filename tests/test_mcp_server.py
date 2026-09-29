import asyncio
import unittest

from src.mcp_server import mcp


class McpServerTests(unittest.TestCase):
    def test_expected_tools_are_registered(self):
        names = {tool.name for tool in asyncio.run(mcp.list_tools())}
        self.assertEqual({"search_knowledge", "answer_question", "get_page_details",
                          "check_document_conflicts"}, names)

    def test_page_resource_template_is_registered(self):
        templates = asyncio.run(mcp.list_resource_templates())
        uris = {str(t.uri_template) for t in templates}
        self.assertIn("meridian://pages/{page_id}", uris)


if __name__ == "__main__":
    unittest.main()
