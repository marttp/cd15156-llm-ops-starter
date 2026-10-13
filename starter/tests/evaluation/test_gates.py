import math
from src.evaluation.gates import METRICS, failures, statistics


def test_complete_result_passes_and_threshold_violation_fails():
    scores = dict.fromkeys(METRICS, .8)
    assert failures(scores, [scores], {"faithfulness": .75}) == []
    assert "faithfulness" in failures(scores, [scores], {"faithfulness": .85})[0]


def test_missing_and_nan_rows_cannot_hide_behind_a_finite_average():
    scores = dict.fromkeys(METRICS, .8)
    row = scores | {"context_precision": float("nan")}
    assert "context_precision" in failures(scores, [scores, row])[0]
    assert failures(scores, [])
    assert failures({}, [scores])


def test_descriptive_statistics_use_the_recorded_rows():
    rows = [dict.fromkeys(METRICS, v) for v in (.4, .8, 1.)]
    observed = statistics(rows)["faithfulness"]
    assert observed["median"] == .8
    assert observed["min"] == .4
    assert observed["max"] == 1.
