"""Fetch pages from a personal Confluence Cloud space into local Markdown.

The connector deliberately ends at the same Page/Markdown boundary used by the
frozen corpus. Chunking, embedding, pgvector ingestion, and RAG remain separate
stages that can be observed and tested independently.
"""

from __future__ import annotations

import argparse
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urljoin, urlparse

import httpx
import yaml
from bs4 import BeautifulSoup


RETRYABLE_STATUS = {429, 500, 502, 503, 504}

STATUS_LABELS = {
    "status-current": "current",
    "status-under-review": "under_review",
    "status-draft": "draft",
    "status-deprecated": "deprecated",
}
AUTHORITY_LABELS = {
    "authority-canonical": "canonical",
    "authority-standard": "standard",
    "authority-draft-only": "draft-only",
    "authority-deprecated": "deprecated",
}
DOCUMENT_TYPE_LABELS = {
    "type-procedure": "procedure",
    "type-checklist": "checklist",
    "type-faq": "faq",
    "type-audit": "audit",
    "type-glossary": "glossary",
    "type-policy": "policy",
    "type-reference": "reference",
}


@dataclass(frozen=True)
class ConfluenceConfig:
    base_url: str
    email: str
    api_token: str
    space_id: str

    @classmethod
    def from_env(cls) -> "ConfluenceConfig":
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass
        names = {
            "base_url": "CONFLUENCE_BASE_URL",
            "email": "CONFLUENCE_EMAIL",
            "api_token": "CONFLUENCE_API_TOKEN",
            "space_id": "CONFLUENCE_SPACE_ID",
        }
        values = {field: os.getenv(name, "").strip() for field, name in names.items()}
        missing = [names[field] for field, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"Missing Confluence configuration: {', '.join(missing)}")
        base_url = values["base_url"].rstrip("/")
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("CONFLUENCE_BASE_URL must be an https:// site URL")
        if not values["space_id"].isdigit():
            raise ValueError("CONFLUENCE_SPACE_ID must be the numeric space ID")
        return cls(base_url, values["email"], values["api_token"], values["space_id"])


def storage_to_markdown(storage: str) -> str:
    """Convert Confluence storage XHTML into deterministic retrieval text."""
    soup = BeautifulSoup(storage or "", "html.parser")
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for code in soup.find_all("code"):
        code.string = f"`{code.get_text(' ', strip=True)}`"
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        level = int(heading.name[1])
        heading.replace_with(f"\n{'#' * level} {heading.get_text(' ', strip=True)}\n")
    for item in soup.find_all("li"):
        item.replace_with(f"\n- {item.get_text(' ', strip=True)}")
    for row in soup.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        row.replace_with("\n| " + " | ".join(cells) + " |\n")
    text = soup.get_text("\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class ConfluenceClient:
    def __init__(self, config: ConfluenceConfig, *, client: httpx.Client | None = None,
                 max_retries: int = 3):
        self.config = config
        self.max_retries = max_retries
        self.client = client or httpx.Client(
            base_url=config.base_url,
            auth=(config.email, config.api_token),
            headers={"Accept": "application/json"},
            timeout=httpx.Timeout(30.0, connect=5.0),
        )
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> "ConfluenceClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    def _get(self, url: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            response = self.client.get(url, params=params)
            if response.status_code not in RETRYABLE_STATUS or attempt == self.max_retries:
                response.raise_for_status()
                return response
            retry_after = response.headers.get("Retry-After", "")
            delay = min(float(retry_after), 10.0) if retry_after.isdigit() else 0.5 * (2 ** attempt)
            time.sleep(delay)
        raise AssertionError("retry loop did not return")

    def iter_pages(self, *, limit: int = 50) -> Iterator[dict[str, Any]]:
        if not 1 <= limit <= 250:
            raise ValueError("limit must be between 1 and 250")
        url = "/wiki/api/v2/pages"
        params: dict[str, Any] | None = {
            "space-id": self.config.space_id,
            "status": "current",
            "body-format": "storage",
            "include-labels": "true",
            "limit": limit,
        }
        while url:
            response = self._get(url, params=params)
            payload = response.json()
            for page in payload.get("results", []):
                # Some Confluence Cloud tenants ignore include-labels on the
                # page-list endpoint. Fetch labels explicitly when omitted.
                if not page_labels(page):
                    page = dict(page)
                    page["labels"] = {"results": self.get_page_labels(str(page["id"]))}
                yield page
            next_url = payload.get("_links", {}).get("next")
            if not next_url:
                break
            resolved = urljoin(self.config.base_url + "/", next_url)
            if urlparse(resolved).netloc != urlparse(self.config.base_url).netloc:
                raise RuntimeError("Confluence pagination attempted to change hosts")
            parsed = urlparse(resolved)
            url = parsed.path + (f"?{parsed.query}" if parsed.query else "")
            params = None

    def get_page_labels(self, page_id: str, *, limit: int = 250) -> list[dict[str, Any]]:
        """Fetch every label attached to one Confluence page."""
        url = f"/wiki/api/v2/pages/{page_id}/labels"
        params: dict[str, Any] | None = {"limit": limit}
        labels: list[dict[str, Any]] = []
        while url:
            response = self._get(url, params=params)
            payload = response.json()
            labels.extend(payload.get("results", []))
            next_url = payload.get("_links", {}).get("next")
            if not next_url:
                break
            resolved = urljoin(self.config.base_url + "/", next_url)
            if urlparse(resolved).netloc != urlparse(self.config.base_url).netloc:
                raise RuntimeError("Confluence label pagination attempted to change hosts")
            parsed = urlparse(resolved)
            url = parsed.path + (f"?{parsed.query}" if parsed.query else "")
            params = None
        return labels


def page_labels(page: dict[str, Any]) -> list[str]:
    """Return normalized label names from either supported v2 response shape."""
    raw_labels = page.get("labels") or []
    if isinstance(raw_labels, dict):
        raw_labels = raw_labels.get("results") or []
    labels = {
        str(item.get("name", "")).strip().lower()
        for item in raw_labels
        if isinstance(item, dict) and item.get("name")
    }
    return sorted(labels)


def governance_metadata(labels: list[str]) -> dict[str, Any]:
    """Translate explicit Confluence governance labels into RAG metadata."""
    label_set = set(labels)
    metadata: dict[str, Any] = {}

    for label, status in STATUS_LABELS.items():
        if label in label_set:
            metadata["status"] = status
            break
    for label, authority in AUTHORITY_LABELS.items():
        if label in label_set:
            metadata["authority_level"] = authority
            break
    for label, document_type in DOCUMENT_TYPE_LABELS.items():
        if label in label_set:
            metadata["document_type"] = document_type
            break
    if "lifecycle-superseded" in label_set:
        metadata["lifecycle"] = "superseded"

    return metadata


def page_document(page: dict[str, Any], config: ConfluenceConfig) -> tuple[str, str]:
    confluence_id = str(page["id"])
    page_id = f"conf-{confluence_id}"
    title = str(page.get("title") or f"Confluence page {confluence_id}")
    version = page.get("version") or {}
    webui = page.get("_links", {}).get("webui", "")
    url = urljoin(config.base_url + "/wiki/", webui.lstrip("/")) if webui else None
    storage = (page.get("body", {}).get("storage", {}) or {}).get("value", "")
    body = storage_to_markdown(storage)
    labels = page_labels(page)
    metadata = {
        "id": page_id,
        "title": title,
        "space": config.space_id,
        "status": page.get("status", "current"),
        "document_type": "confluence_page",
        "labels": labels,
        "last_updated": version.get("createdAt"),
        "confluence_page_id": confluence_id,
        "confluence_version": version.get("number"),
        "source": "confluence_cloud",
        "url": url,
    }
    metadata.update(governance_metadata(labels))
    clean_metadata = {key: value for key, value in metadata.items() if value is not None}
    frontmatter = yaml.safe_dump(clean_metadata, sort_keys=False, allow_unicode=True).strip()
    return page_id, f"---\n{frontmatter}\n---\n\n# {title}\n\n{body}\n"


def sync_pages(client: ConfluenceClient, output: Path, *, limit: int = 50,
               dry_run: bool = False, prune_missing: bool = False) -> dict[str, int]:
    fetched = written = unchanged = 0
    seen_page_ids: set[str] = set()
    if not dry_run:
        output.mkdir(parents=True, exist_ok=True)
    for page in client.iter_pages(limit=limit):
        fetched += 1
        page_id, document = page_document(page, client.config)
        seen_page_ids.add(page_id)
        target = output / f"{page_id}.md"
        if target.exists() and target.read_text(encoding="utf-8") == document:
            unchanged += 1
        elif not dry_run:
            target.write_text(document, encoding="utf-8")
            written += 1
    removed = 0
    if prune_missing and not dry_run and output.exists():
        for target in output.glob("conf-*.md"):
            if target.stem not in seen_page_ids:
                target.unlink()
                removed += 1
    result = {"fetched": fetched, "written": written, "unchanged": unchanged}
    if prune_missing:
        result["removed"] = removed
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync a personal Confluence Cloud space")
    parser.add_argument("--output", type=Path, default=Path("data/confluence_pages"))
    parser.add_argument("--limit", type=int, default=50, help="API page size")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = ConfluenceConfig.from_env()
    with ConfluenceClient(config) as client:
        result = sync_pages(client, args.output, limit=args.limit, dry_run=args.dry_run)
    print(" ".join(f"{key}={value}" for key, value in result.items()))
    print(f"output={args.output} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
