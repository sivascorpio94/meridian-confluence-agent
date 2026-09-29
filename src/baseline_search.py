"""Stage 1: dependency-light lexical retrieval over the frozen corpus.

This intentionally does not use an LLM, embeddings, LangChain, document
authority, or conflict resolution. It gives later RAG stages a fair baseline.
"""

from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[_-][a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass(frozen=True)
class Page:
    page_id: str
    title: str
    metadata: dict
    body: str
    tokens: tuple[str, ...]


def load_page(path: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid frontmatter in {path}")
    metadata = yaml.safe_load(match.group(1))
    body = match.group(2)

    # Title and labels receive repetition-based lexical weight. This remains a
    # keyword baseline: no source reliability fields influence ranking.
    labels = " ".join(metadata.get("labels", []))
    searchable = f"{metadata['title']} {metadata['title']} {labels} {body}"
    return Page(
        page_id=metadata["id"],
        title=metadata["title"],
        metadata=metadata,
        body=body,
        tokens=tuple(tokenize(searchable)),
    )


def load_corpus(directory: Path) -> list[Page]:
    pages = [load_page(path) for path in sorted(directory.glob("*.md"))]
    if not pages:
        raise ValueError(f"No Markdown pages found in {directory}")
    return pages


class BM25Search:
    def __init__(self, pages: Iterable[Page], k1: float = 1.5, b: float = 0.75):
        self.pages = list(pages)
        self.k1 = k1
        self.b = b
        self.avgdl = sum(len(page.tokens) for page in self.pages) / len(self.pages)
        self.document_frequency: dict[str, int] = {}
        for page in self.pages:
            for token in set(page.tokens):
                self.document_frequency[token] = self.document_frequency.get(token, 0) + 1

    def _idf(self, term: str) -> float:
        n = len(self.pages)
        df = self.document_frequency.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def _score(self, query_tokens: list[str], page: Page) -> float:
        frequencies: dict[str, int] = {}
        for token in page.tokens:
            frequencies[token] = frequencies.get(token, 0) + 1
        score = 0.0
        for term in query_tokens:
            tf = frequencies.get(term, 0)
            if not tf:
                continue
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * len(page.tokens) / self.avgdl)
            score += self._idf(term) * numerator / denominator
        return score

    def search(self, query: str, limit: int = 5) -> list[tuple[Page, float]]:
        query_tokens = tokenize(query)
        scored = [(page, self._score(query_tokens, page)) for page in self.pages]
        return sorted(scored, key=lambda item: (-item[1], item[0].page_id))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Meridian pages using lexical BM25")
    parser.add_argument("query", help="Natural-language search query")
    parser.add_argument("--corpus", type=Path, default=Path("data/raw_pages"))
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    engine = BM25Search(load_corpus(args.corpus))
    for rank, (page, score) in enumerate(engine.search(args.query, args.limit), start=1):
        print(f"{rank}. {page.page_id} | {score:.4f} | {page.title}")


if __name__ == "__main__":
    main()
