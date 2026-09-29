"""Stage 3: transparent, heading-aware chunking for the Markdown corpus.

The implementation deliberately avoids LangChain so the transformation from a
Confluence-like page to embedding-ready records remains visible and testable.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from src.baseline_search import Page, load_corpus


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    """One retrieval unit plus the metadata needed for filtering and citations."""

    chunk_id: str
    page_id: str
    title: str
    section_path: tuple[str, ...]
    text: str
    embedding_text: str
    metadata: dict


def _json_safe(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "root"


def _sections(body: str) -> list[tuple[tuple[str, ...], str]]:
    """Split Markdown by headings while retaining the current heading hierarchy."""
    matches = list(HEADING_RE.finditer(body))
    if not matches:
        return [((), body.strip())]

    sections: list[tuple[tuple[str, ...], str]] = []
    hierarchy: list[str] = []
    preamble = body[: matches[0].start()].strip()
    if preamble:
        sections.append(((), preamble))

    for index, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        hierarchy = hierarchy[: level - 1]
        hierarchy.append(heading)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[match.end() : end].strip()
        if content:
            sections.append((tuple(hierarchy), content))
    return sections


def _split_long_text(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    """Create bounded windows, preferring paragraph and sentence boundaries."""
    pieces: list[str] = []
    start = 0
    while start < len(text):
        hard_end = min(start + max_chars, len(text))
        end = hard_end
        if hard_end < len(text):
            candidates = [
                text.rfind("\n\n", start + max_chars // 2, hard_end),
                text.rfind(". ", start + max_chars // 2, hard_end),
                text.rfind("\n", start + max_chars // 2, hard_end),
                text.rfind(" ", start + max_chars // 2, hard_end),
            ]
            boundary = max(candidates)
            if boundary > start:
                end = boundary + (2 if text[boundary : boundary + 2] == ". " else 0)
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        next_start = max(end - overlap_chars, start + 1)
        whitespace = text.find(" ", next_start, end)
        start = whitespace + 1 if whitespace != -1 else next_start
    return pieces


def chunk_page(page: Page, max_chars: int = 1_400, overlap_chars: int = 200) -> list[Chunk]:
    if max_chars < 200:
        raise ValueError("max_chars must be at least 200")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be between 0 and max_chars - 1")

    chunks: list[Chunk] = []
    page_metadata = _json_safe(page.metadata)
    for section_path, content in _sections(page.body):
        heading = " > ".join(section_path) if section_path else "Overview"
        prefix = f"Page: {page.title}\nSection: {heading}\n\n"
        content_limit = max_chars - len(prefix)
        if content_limit < 100:
            raise ValueError("max_chars is too small for the title and section context")

        for part in _split_long_text(content, content_limit, overlap_chars):
            sequence = len(chunks) + 1
            chunk_id = f"{page.page_id}::{_slug(heading)}::{sequence:03d}"
            metadata = {
                **page_metadata,
                "page_id": page.page_id,
                "source_file": f"{page.page_id}.md",
                "section_path": list(section_path),
                "chunk_sequence": sequence,
            }
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    page_id=page.page_id,
                    title=page.title,
                    section_path=section_path,
                    text=part,
                    embedding_text=prefix + part,
                    metadata=metadata,
                )
            )
    return chunks


def chunk_corpus(
    pages: Iterable[Page], max_chars: int = 1_400, overlap_chars: int = 200
) -> list[Chunk]:
    return [
        chunk
        for page in pages
        for chunk in chunk_page(page, max_chars=max_chars, overlap_chars=overlap_chars)
    ]


def write_jsonl(chunks: Iterable[Chunk], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk Meridian Markdown pages")
    parser.add_argument("--corpus", type=Path, default=Path("data/raw_pages"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--max-chars", type=int, default=1_400)
    parser.add_argument("--overlap-chars", type=int, default=200)
    parser.add_argument("--preview", type=int, default=3)
    args = parser.parse_args()

    pages = load_corpus(args.corpus)
    chunks = chunk_corpus(pages, args.max_chars, args.overlap_chars)
    count = write_jsonl(chunks, args.output)

    print(f"pages={len(pages)} chunks={count} output={args.output}")
    for chunk in chunks[: args.preview]:
        print(
            f"\n{chunk.chunk_id} | chars={len(chunk.embedding_text)} "
            f"| section={' > '.join(chunk.section_path) or 'Overview'}"
        )
        print(chunk.embedding_text[:300].replace("\n", " "))


if __name__ == "__main__":
    main()
