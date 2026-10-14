"""Reject incomplete evaluations and regressions without another model call."""

import math

METRICS = ("faithfulness", "answer_relevancy", "context_recall", "context_precision")


def failures(aggregate: dict, rows: list[dict], thresholds: dict | None = None) -> list[str]:
    errors = []
    if not rows:
        errors.append("evaluation has no rows")
    for metric in METRICS:
        values = [aggregate.get(metric)] + [row.get(metric) for row in rows]
        if any(not isinstance(v, (float, int)) or not math.isfinite(v) or not 0 <= v <= 1 for v in values):
            errors.append(f"{metric}: missing, non-finite or out-of-range score")
    for metric, floor in (thresholds or {}).items():
        if not isinstance(floor, (int, float)) or not math.isfinite(floor):
            errors.append(f"{metric}: threshold must be finite")
            continue
        actual = aggregate.get(metric)
        if actual is None or not math.isfinite(actual) or actual < floor:
            errors.append(f"{metric}: actual={actual}, minimum={floor}")
    return errors


def statistics(rows: list[dict]) -> dict:
    import pandas as pd
    frame = pd.DataFrame(rows)
    return {metric: {"median": float(frame[metric].median()), "p10": float(frame[metric].quantile(.1)), "min": float(frame[metric].min()), "max": float(frame[metric].max())} for metric in METRICS if metric in frame}
