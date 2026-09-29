"""Embed a query and retrieve its nearest chunks from pgvector."""

from __future__ import annotations

import argparse

from src.bedrock_embeddings import BedrockEmbeddingClient
from src.vector_store import connect, similarity_search


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic search over Meridian chunks")
    parser.add_argument("query")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    query = BedrockEmbeddingClient(region=args.region).embed(args.query)
    connection = connect()
    try:
        hits = similarity_search(connection, query.vector, args.limit)
    finally:
        connection.close()

    for rank, hit in enumerate(hits, start=1):
        section = " > ".join(hit.section_path) or "Overview"
        print(
            f"{rank}. {hit.page_id} | similarity={hit.similarity:.4f} "
            f"| {hit.title} | {section}"
        )
        print(f"   {hit.content[:220].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()

