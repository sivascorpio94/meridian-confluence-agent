"""Embed JSONL chunks with Bedrock and upsert them into pgvector."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from src.bedrock_embeddings import BedrockEmbeddingClient
from src.vector_store import connect, existing_hashes, initialize_schema, upsert_chunk


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def embedding_fingerprint(chunk: dict, model_id: str, dimensions: int) -> str:
    material = f"{model_id}\0{dimensions}\0{chunk['embedding_text']}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def ingest_chunks(chunks: list[dict], *, region: str = "us-east-2",
                  schema: Path = Path("sql/001_document_chunks.sql"),
                  delay: float = 0.05, embedding_client=None,
                  connection_factory=connect) -> dict[str, int]:
    """Embed and upsert chunks, skipping records with unchanged fingerprints."""
    client = embedding_client or BedrockEmbeddingClient(region=region)
    connection = connection_factory()
    try:
        initialize_schema(connection, schema)
        hashes = existing_hashes(connection, [chunk["chunk_id"] for chunk in chunks])
        inserted = skipped = tokens = 0
        for index, chunk in enumerate(chunks, start=1):
            fingerprint = embedding_fingerprint(chunk, client.model_id, client.dimensions)
            if hashes.get(chunk["chunk_id"]) == fingerprint:
                skipped += 1
                print(f"[{index}/{len(chunks)}] skip {chunk['chunk_id']}")
                continue

            result = client.embed(chunk["embedding_text"])
            upsert_chunk(connection, chunk, fingerprint, result)
            inserted += 1
            tokens += result.input_token_count
            print(f"[{index}/{len(chunks)}] upsert {chunk['chunk_id']} tokens={result.input_token_count}")
            if delay:
                time.sleep(delay)
        return {"inserted_or_updated": inserted, "skipped": skipped, "input_tokens": tokens}
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Meridian chunks into pgvector")
    parser.add_argument("--chunks", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--schema", type=Path, default=Path("sql/001_document_chunks.sql"))
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    chunks = load_chunks(args.chunks)
    if args.limit is not None:
        chunks = chunks[: args.limit]

    result = ingest_chunks(
        chunks, region=args.region, schema=args.schema, delay=args.delay
    )
    print("complete " + " ".join(f"{key}={value}" for key, value in result.items()))


if __name__ == "__main__":
    main()
