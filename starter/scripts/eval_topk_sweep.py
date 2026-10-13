"""Run RAGAS evaluation at three `top_k` values and print a comparison table.

Sweeps `top_k ∈ {3, 5, 10}` against `data/golden_test_set.csv` and
emits a markdown table the learner can paste into `WRITEUP.template.md`
§2 — replacing the "edit pipeline.py + restart + re-run × 3" cycle the
rubric used to require.

Cost note: this runs RAGAS three times, so expect ~3× the spend of one
`make eval` invocation (~$0.06 total at current OpenAI pricing as of
April 2026). Wall clock is ~5–10 min depending on the test-set size
and whether the Vocareum proxy is in use.

Usage:
    set -a; source .env; set +a   # if your .env isn't already loaded
    make eval-topk-sweep
    # or
    uv run --no-project python scripts/eval_topk_sweep.py --topks 1,3,5,10
"""

import argparse
import json
import sys
from pathlib import Path

from src.evaluation import evaluate_pipeline, load_golden_set, summarize
from src.evaluation.gates import failures, statistics

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "data" / "golden_test_set.csv"
DEFAULT_TOPKS = (3, 5, 10)
METRIC_COLUMNS = ("faithfulness", "answer_relevancy", "context_recall", "context_precision")


def _parse_topks(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _format_row(top_k: int, scored: dict[str, float]) -> str:
    cells = [f"{top_k}"]
    for metric in METRIC_COLUMNS:
        value = scored.get(metric)
        cells.append(f"{value:.3f}" if value is not None else "—")
    return "| " + " | ".join(cells) + " |"


def _render_markdown(rows: list[tuple[int, dict[str, float]]]) -> str:
    header = "| top_k | " + " | ".join(METRIC_COLUMNS) + " |"
    sep = "|-------|" + "|".join("-" * (len(m) + 2) for m in METRIC_COLUMNS) + "|"
    body = [_format_row(top_k, scored) for top_k, scored in rows]
    return "\n".join([header, sep, *body])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sweep top_k values and emit a RAGAS comparison table."
    )
    parser.add_argument(
        "--golden", type=Path, default=GOLDEN_PATH,
        help=f"Golden test set CSV (default: {GOLDEN_PATH}).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Run only the first N questions per sweep value (default: all).",
    )
    parser.add_argument(
        "--topks", type=_parse_topks, default=list(DEFAULT_TOPKS),
        help=f"Comma-separated top_k values to sweep (default: {','.join(map(str, DEFAULT_TOPKS))}).",
    )
    parser.add_argument(
        "--max-workers", type=int, default=None,
        help=(
            "Cap RAGAS executor concurrency. Default lets RAGAS use 16. "
            "Set to 1 when running through a contended proxy (e.g. Vocareum "
            "from a local CPU-only host) — trades wall-clock for completeness "
            "by avoiding parallel-load timeouts that produce nan metric cells."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("evidence/evaluation/sweep"))
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    golden = load_golden_set(args.golden)
    if args.limit is not None:
        golden = golden[: args.limit]

    rows: list[tuple[int, dict[str, float]]] = []
    for top_k in args.topks:
        print(f"==> Sweeping top_k={top_k} over {len(golden)} questions ...", file=sys.stderr)
        result = evaluate_pipeline(golden, top_k=top_k, max_workers=args.max_workers)
        aggregate = summarize(result)
        scored_rows = result.to_pandas().to_dict("records")
        (args.output_dir / f"top_k_{top_k}.json").write_text(json.dumps({"aggregate": aggregate, "rows": scored_rows, "statistics": statistics(scored_rows), "top_k": top_k}, indent=2, default=str))
        errors = failures(aggregate, scored_rows)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 2
        rows.append((top_k, aggregate))

    print()
    table = _render_markdown(rows)
    (args.output_dir / "comparison.md").write_text(table + "\n")
    print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
