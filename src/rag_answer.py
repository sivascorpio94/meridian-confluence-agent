"""Stage 6: end-to-end manual RAG without LangChain."""

from __future__ import annotations

import argparse

from src.bedrock_chat import DEFAULT_CHAT_MODEL_ID
from src.rag_context import (
    SYSTEM_PROMPT,
    citation_warnings,
)
from src.rag_pipeline import answer_question


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer a Meridian question with manual RAG")
    parser.add_argument("question")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--model", default=DEFAULT_CHAT_MODEL_ID)
    parser.add_argument("--retrieve", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--max-tokens", type=int, default=250)
    parser.add_argument(
        "--source", choices=("all", "confluence_cloud", "frozen_corpus"),
        default="all", help="Restrict retrieval to one corpus",
    )
    parser.add_argument("--show-context", action="store_true")
    args = parser.parse_args()

    result = answer_question(
        args.question,
        region=args.region,
        model_id=args.model,
        retrieve=args.retrieve,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        source_scope=args.source,
        progress=lambda message: print(message, flush=True),
    )

    if args.show_context:
        print("=== SYSTEM PROMPT ===")
        print(SYSTEM_PROMPT)
        print("\n=== USER PROMPT ===")
        print(result.user_prompt)
        print("\n=== MODEL ANSWER ===")

    print(result.answer.text)

    warnings = (
        citation_warnings(result.answer.text, result.evidence.page_ids)
        if result.decision.status == "answered"
        else ()
    )
    if warnings:
        print("\nVALIDATION WARNINGS:")
        for warning in warnings:
            print(f"- {warning}")

    print(
        f"\nmodel={result.answer.model_id} input_tokens={result.answer.input_tokens} "
        f"output_tokens={result.answer.output_tokens} latency_ms={result.answer.latency_ms} "
        f"stop_reason={result.answer.stop_reason}"
    )
    print(
        "evidence="
        f"recommended:{','.join(item.hit.page_id for item in result.evidence.recommended)} "
        f"conflicts:{','.join(item.hit.page_id for item in result.evidence.conflicts)}"
    )
    print(
        f"timings_ms=embedding:{result.timings.embedding_ms} "
        f"retrieval:{result.timings.retrieval_ms} "
        f"generation:{result.timings.generation_ms} total:{result.timings.total_ms}"
    )
    print(
        f"decision={result.decision.status} "
        f"max_semantic={result.decision.max_semantic_score:.4f} "
        f"threshold={result.decision.minimum_similarity:.2f}"
    )


if __name__ == "__main__":
    main()
