"""Deterministic Stage 7 evaluation for retrieval, trust, and grounded answers."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.rag_context import CITATION_RE
from src.rag_pipeline import answer_question


def contains_all(text: str, terms: list[str]) -> bool:
    normalized = text.casefold()
    return all(term.casefold() in normalized for term in terms)


def score_case(case: dict, result) -> dict:
    ranked_pages = [item.hit.page_id for item in result.ranked]
    recommended_pages = [item.hit.page_id for item in result.evidence.recommended]
    conflict_pages = [item.hit.page_id for item in result.evidence.conflicts]
    citations = sorted(set(CITATION_RE.findall(result.answer.text)))
    relevant = set(case["relevant_pages"])
    misleading = set(case["misleading_pages"])
    preferred = set(case["preferred_pages"])
    required_citations = set(case.get("required_citations", []))
    expected_warnings = set(case.get("expected_warning_pages", []))

    unique_ranked = list(dict.fromkeys(ranked_pages))
    metrics = {
        "relevant_hit_at_5": bool(relevant.intersection(unique_ranked[:5])),
        "preferred_top_1": bool(unique_ranked and unique_ranked[0] in preferred),
        "misleading_excluded_from_top_1": not bool(
            unique_ranked and unique_ranked[0] in misleading
        ),
        "required_answer_terms": contains_all(
            result.answer.text, case.get("required_answer_terms", [])
        ),
        "required_citations": required_citations.issubset(citations),
        "expected_conflicts_detected": expected_warnings.issubset(conflict_pages),
        "citations_grounded": set(citations).issubset(result.evidence.page_ids),
    }
    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "passed": all(metrics.values()),
        "metrics": metrics,
        "ranked_pages": ranked_pages,
        "recommended_pages": recommended_pages,
        "conflict_pages": conflict_pages,
        "citations": citations,
        "answer": result.answer.text,
        "input_tokens": result.answer.input_tokens,
        "output_tokens": result.answer.output_tokens,
        "timings_ms": result.timings.__dict__,
    }


def write_markdown(report: dict, path: Path) -> None:
    totals = report["summary"]
    lines = [
        "# Meridian RAG Evaluation",
        "",
        f"- Cases passed: **{totals['passed_cases']}/{totals['total_cases']}**",
        f"- Checks passed: **{totals['passed_checks']}/{totals['total_checks']}**",
        f"- Average latency: **{totals['average_latency_ms']} ms**",
        f"- Total tokens: **{totals['total_tokens']}**",
        "",
        "| Case | Category | Result | Failed checks | Latency |",
        "|---|---|---:|---|---:|",
    ]
    for item in report["cases"]:
        failed = [name for name, passed in item["metrics"].items() if not passed]
        lines.append(
            f"| {item['id']} | {item['category']} | "
            f"{'PASS' if item['passed'] else 'FAIL'} | "
            f"{', '.join(failed) or 'none'} | {item['timings_ms']['total_ms']} ms |"
        )
    lines.extend(["", "## Case details", ""])
    for item in report["cases"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"**Question:** {item['question']}",
                "",
                f"**Ranked pages:** {', '.join(item['ranked_pages'])}",
                "",
                f"**Answer:** {item['answer']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the complete Meridian RAG pipeline")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--retrieve", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=250)
    parser.add_argument("--case", help="Run one case ID instead of the full suite")
    parser.add_argument("--output", type=Path, default=Path("eval/results"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    cases = yaml.safe_load((root / "eval/questions.yaml").read_text(encoding="utf-8"))
    if args.case:
        cases = [case for case in cases if case["id"] == args.case]
        if not cases:
            raise SystemExit(f"Unknown evaluation case: {args.case}")

    scored = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['id']}", flush=True)
        result = answer_question(
            case["question"],
            region=args.region,
            retrieve=args.retrieve,
            max_tokens=args.max_tokens,
            source_scope="frozen_corpus",
        )
        item = score_case(case, result)
        scored.append(item)
        failed = [name for name, passed in item["metrics"].items() if not passed]
        print(f"  {'PASS' if item['passed'] else 'FAIL'} ({', '.join(failed) or 'all checks'})")

    checks = [passed for item in scored for passed in item["metrics"].values()]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "region": args.region,
            "retrieve": args.retrieve,
            "max_tokens": args.max_tokens,
        },
        "summary": {
            "total_cases": len(scored),
            "passed_cases": sum(item["passed"] for item in scored),
            "total_checks": len(checks),
            "passed_checks": sum(checks),
            "average_latency_ms": round(
                sum(item["timings_ms"]["total_ms"] for item in scored) / len(scored)
            ),
            "total_tokens": sum(
                item["input_tokens"] + item["output_tokens"] for item in scored
            ),
        },
        "cases": scored,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    json_path = args.output / "rag-evaluation.json"
    markdown_path = args.output / "rag-evaluation.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, markdown_path)
    print(f"\nCases: {report['summary']['passed_cases']}/{report['summary']['total_cases']}")
    print(f"Checks: {report['summary']['passed_checks']}/{report['summary']['total_checks']}")
    print(f"Reports: {json_path}, {markdown_path}")


if __name__ == "__main__":
    main()
