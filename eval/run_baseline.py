from pathlib import Path

import yaml

from src.baseline_search import BM25Search, load_corpus


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cases = yaml.safe_load((root / "eval/questions.yaml").read_text())
    engine = BM25Search(load_corpus(root / "data/raw_pages"))

    recall_hits = 0
    misleading_hits = 0
    for case in cases:
        results = engine.search(case["question"], limit=5)
        ids = [page.page_id for page, _ in results]
        expected = set(case["relevant_pages"])
        misleading = set(case["misleading_pages"])
        found = bool(expected.intersection(ids))
        has_misleading = bool(misleading.intersection(ids))
        recall_hits += int(found)
        misleading_hits += int(has_misleading)
        print(f"{case['id']}: top5={ids} relevant_hit={found} misleading_hit={has_misleading}")

    total = len(cases)
    print(f"\nRecall@5 (at least one relevant page): {recall_hits}/{total}")
    print(f"Queries with misleading page in top 5: {misleading_hits}/{total}")


if __name__ == "__main__":
    main()

