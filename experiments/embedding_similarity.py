"""Generate a few embeddings and compare their semantic similarity."""

from __future__ import annotations

import argparse
from itertools import combinations

from src.bedrock_embeddings import BedrockEmbeddingClient, cosine_similarity


SENTENCES = {
    "query": "I need read-only access to the Mosaic customer console.",
    "semantic_match": "Request the MOSAIC_UI_VIEWER role to view customer records.",
    "keyword_trap": "Request remote access for your company laptop using the VPN client.",
    "unrelated": "Employees can order a laptop monitor from the hardware catalog.",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Bedrock embedding similarity experiment")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--dimensions", type=int, default=1024)
    args = parser.parse_args()

    client = BedrockEmbeddingClient(region=args.region, dimensions=args.dimensions)
    results = {name: client.embed(text) for name, text in SENTENCES.items()}

    first = next(iter(results.values()))
    print(f"model={first.model_id}")
    print(f"dimensions={len(first.vector)}")
    for name, result in results.items():
        print(f"{name}: tokens={result.input_token_count} text={SENTENCES[name]}")

    print("\nCosine similarities:")
    for left_name, right_name in combinations(SENTENCES, 2):
        score = cosine_similarity(
            results[left_name].vector,
            results[right_name].vector,
        )
        print(f"{left_name:16} <-> {right_name:16} = {score:.4f}")


if __name__ == "__main__":
    main()

