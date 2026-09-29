"""One-command Confluence sync, governed selection, chunking, and ingestion."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from src.baseline_search import Page, load_corpus
from src.chunking import chunk_corpus, write_jsonl
from src.confluence_sync import ConfluenceClient, ConfluenceConfig, sync_pages
from src.ingest import ingest_chunks
from src.vector_store import connect, prune_source_chunks


GOVERNANCE_PREFIXES = ("status-", "authority-", "type-", "lifecycle-")


def is_governed(page: Page) -> bool:
    """Include explicitly governed knowledge; exclude unlabeled templates/noise."""
    labels = page.metadata.get("labels") or []
    return any(str(label).startswith(GOVERNANCE_PREFIXES) for label in labels)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh live Confluence knowledge")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--pages", type=Path, default=Path("data/confluence_pages"))
    parser.add_argument(
        "--chunks", type=Path, default=Path("data/processed/confluence_chunks.jsonl")
    )
    parser.add_argument("--api-limit", type=int, default=50)
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--no-prune", action="store_true")
    args = parser.parse_args()

    config = ConfluenceConfig.from_env()
    with ConfluenceClient(config) as client:
        sync_result = sync_pages(
            client, args.pages, limit=args.api_limit, prune_missing=True
        )

    all_pages = load_corpus(args.pages)
    selected = [page for page in all_pages if is_governed(page)]
    excluded = [page for page in all_pages if not is_governed(page)]
    if not selected:
        raise RuntimeError(
            "No governed Confluence pages found; add status-, authority-, type-, "
            "or lifecycle- labels before refreshing"
        )

    chunks = chunk_corpus(selected)
    write_jsonl(chunks, args.chunks)
    chunk_dicts = [json.loads(json.dumps(asdict(chunk), default=str)) for chunk in chunks]
    ingest_result = ingest_chunks(
        chunk_dicts, region=args.region, delay=args.delay
    )

    pruned = 0
    if not args.no_prune:
        connection = connect()
        try:
            pruned = prune_source_chunks(
                connection, [chunk.chunk_id for chunk in chunks]
            )
        finally:
            connection.close()

    print(
        "refresh_complete "
        f"fetched={sync_result['fetched']} synced={sync_result['written']} "
        f"unchanged_pages={sync_result['unchanged']} "
        f"removed_pages={sync_result['removed']} selected_pages={len(selected)} "
        f"excluded_pages={len(excluded)} chunks={len(chunks)} "
        f"embedded={ingest_result['inserted_or_updated']} "
        f"skipped_embeddings={ingest_result['skipped']} pruned_chunks={pruned}"
    )
    if excluded:
        print("excluded=" + ",".join(page.page_id for page in excluded))


if __name__ == "__main__":
    main()
