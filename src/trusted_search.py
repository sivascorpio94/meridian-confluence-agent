"""Semantic retrieval followed by explainable trust-aware reranking."""

from __future__ import annotations

import argparse

from src.bedrock_embeddings import BedrockEmbeddingClient
from src.reranking import rerank
from src.vector_store import connect, load_page_metadata, similarity_search


def main() -> None:
    parser = argparse.ArgumentParser(description="Trust-aware Meridian search")
    parser.add_argument("query")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--retrieve", type=int, default=15)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--source", choices=("all", "confluence_cloud", "frozen_corpus"),
        default="all", help="Restrict retrieval to one corpus",
    )
    args = parser.parse_args()

    query_embedding = BedrockEmbeddingClient(region=args.region).embed(args.query)
    connection = connect()
    try:
        candidates = similarity_search(
            connection, query_embedding.vector, args.retrieve, args.source
        )
        metadata = load_page_metadata(connection, args.source)
    finally:
        connection.close()

    results = rerank(args.query, candidates, metadata, limit=args.limit)
    for rank, result in enumerate(results, start=1):
        hit = result.hit
        section = " > ".join(hit.section_path) or "Overview"
        print(
            f"{rank}. {hit.page_id} | final={result.final_score:.4f} "
            f"| semantic={result.semantic_score:.4f} "
            f"| metadata={result.metadata_adjustment:+.2f}"
        )
        print(f"   {hit.title} | {section}")
        print(f"   reasons: {'; '.join(result.reasons)}")
        if result.warnings:
            print(f"   WARNING: {'; '.join(result.warnings)}")


if __name__ == "__main__":
    main()
