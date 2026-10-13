"""Measure guarded semantic-cache hits and an explicit wrong-product probe."""

import json
from pathlib import Path

from src.cache.semantic import clear, _collection
from src.config import settings
from src.gateway.routes import QueryRequest, query
from src.tracing import init_tracing, flush


def main():
    init_tracing()
    settings.semantic_cache_enabled = True
    questions = [
        "What is the weight of the baseline control paddle?",
        "How heavy is the baseline control paddle?",
        "How much does the baseline control paddle weigh?",
        "Tell me the weight of the baseline control paddle.",
        "What does the baseline control paddle weigh in ounces?",
        "Give the baseline control paddle weight in oz.",
    ]
    results = []
    try:
        for threshold in (.85, .90, .95):
            clear()
            settings.semantic_cache_threshold = threshold
            rows = []
            for question in questions:
                response = query(QueryRequest(question=question))
                assert response.blocked_by is None and response.sources, response
                rows.append({"question": question, "response": response.model_dump()})
            probe = "How heavy is the baseline power paddle?"
            wrong_product = query(QueryRequest(question=probe))
            results.append({
                "threshold": threshold,
                "hits": sum(row["response"]["cached"] for row in rows),
                "rows": rows,
                "wrong_product_probe": {"question": probe, "response": wrong_product.model_dump(), "expected_weight": "8.3", "false_positive": wrong_product.cached and "8.3" not in wrong_product.answer},
                "cache_collection": _collection().get(limit=10, include=["metadatas", "documents"]),
            })
        output = Path("evidence/cache/results.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(results, indent=2))
        print(json.dumps([{k: row[k] for k in ("threshold", "hits")} | {"false_positive": row["wrong_product_probe"]["false_positive"]} for row in results], indent=2))
        assert any(row["hits"] >= 3 for row in results), "No threshold demonstrated at least three cache hits."
    finally:
        flush()


if __name__ == "__main__":
    main()
