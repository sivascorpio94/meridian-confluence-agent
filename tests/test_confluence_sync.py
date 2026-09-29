import tempfile
import unittest
from pathlib import Path

import httpx

from src.baseline_search import load_page
from src.confluence_sync import (
    ConfluenceClient,
    ConfluenceConfig,
    governance_metadata,
    page_labels,
    page_document,
    storage_to_markdown,
    sync_pages,
)


CONFIG = ConfluenceConfig(
    "https://meridian-demo.atlassian.net", "demo@example.com", "secret", "12345"
)


def response(page_id: str, *, next_url: str | None = None) -> dict:
    links = {"webui": f"/spaces/DEMO/pages/{page_id}"}
    payload = {
        "results": [{
            "id": page_id,
            "status": "current",
            "title": f"Page {page_id}",
            "body": {"storage": {"value": "<h2>Access</h2><p>Use <code>VIEWER</code>.</p>"}},
            "version": {"number": 2, "createdAt": "2026-09-28T10:00:00Z"},
            "labels": {"results": [
                {"id": "1", "name": "status-current", "prefix": "global"},
                {"id": "2", "name": "authority-canonical", "prefix": "global"},
                {"id": "3", "name": "type-procedure", "prefix": "global"},
            ]},
            "_links": links,
        }],
        "_links": {},
    }
    if next_url:
        payload["_links"]["next"] = next_url
    return payload


class ConfluenceSyncTests(unittest.TestCase):
    def test_storage_to_markdown_preserves_retrieval_structure(self):
        text = storage_to_markdown(
            "<h2>Steps</h2><ol><li>Open catalog</li><li>Select <code>VIEWER</code></li></ol>"
        )
        self.assertIn("## Steps", text)
        self.assertIn("- Open catalog", text)
        self.assertIn("`VIEWER`", text)

    def test_cursor_pagination_and_authentication(self):
        seen = []

        def handler(request):
            seen.append(request)
            if "cursor=next" in str(request.url):
                return httpx.Response(200, json=response("200"))
            return httpx.Response(200, json=response(
                "100", next_url="/wiki/api/v2/pages?cursor=next"
            ))

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(
            base_url=CONFIG.base_url, auth=(CONFIG.email, CONFIG.api_token), transport=transport
        )
        client = ConfluenceClient(CONFIG, client=http_client)
        pages = list(client.iter_pages(limit=25))

        self.assertEqual(["100", "200"], [page["id"] for page in pages])
        self.assertEqual("12345", seen[0].url.params["space-id"])
        self.assertEqual("true", seen[0].url.params["include-labels"])
        self.assertTrue(seen[0].headers["Authorization"].startswith("Basic "))

    def test_fetches_labels_separately_when_page_list_omits_them(self):
        def handler(request):
            if request.url.path.endswith("/pages/100/labels"):
                return httpx.Response(200, json={
                    "results": [{"id": "1", "name": "authority-canonical"}],
                    "_links": {},
                })
            payload = response("100")
            del payload["results"][0]["labels"]
            return httpx.Response(200, json=payload)

        http_client = httpx.Client(
            base_url=CONFIG.base_url,
            auth=(CONFIG.email, CONFIG.api_token),
            transport=httpx.MockTransport(handler),
        )
        client = ConfluenceClient(CONFIG, client=http_client)
        pages = list(client.iter_pages())

        self.assertEqual(
            "authority-canonical",
            pages[0]["labels"]["results"][0]["name"],
        )

    def test_export_is_loadable_and_incremental(self):
        page = response("100")["results"][0]
        page_id, document = page_document(page, CONFIG)
        self.assertEqual("conf-100", page_id)
        self.assertNotIn("secret", document)

        class FakeClient:
            config = CONFIG

            def iter_pages(self, limit=50):
                yield page

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = sync_pages(FakeClient(), output)
            second = sync_pages(FakeClient(), output)
            loaded = load_page(output / "conf-100.md")

        self.assertEqual({"fetched": 1, "written": 1, "unchanged": 0}, first)
        self.assertEqual({"fetched": 1, "written": 0, "unchanged": 1}, second)
        self.assertEqual("conf-100", loaded.page_id)
        self.assertEqual("canonical", loaded.metadata["authority_level"])
        self.assertEqual("procedure", loaded.metadata["document_type"])

    def test_labels_map_to_governance_without_inventing_authority(self):
        page = {"labels": [
            {"name": "status-under-review"},
            {"name": "lifecycle-superseded"},
            {"name": "type-faq"},
        ]}
        labels = page_labels(page)
        metadata = governance_metadata(labels)

        self.assertEqual("under_review", metadata["status"])
        self.assertEqual("superseded", metadata["lifecycle"])
        self.assertEqual("faq", metadata["document_type"])
        self.assertNotIn("authority_level", metadata)


if __name__ == "__main__":
    unittest.main()
    governance_metadata,
    page_labels,
