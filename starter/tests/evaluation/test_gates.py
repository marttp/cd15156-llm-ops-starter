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


def test_saved_result_gate_runs_without_a_provider_key(tmp_path):
    import os, json, subprocess
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    scores = dict.fromkeys(METRICS, .8)
    saved = tmp_path / 'result.json'
    saved.write_text(json.dumps({'aggregate': scores, 'rows': [scores]}))
    env = {**os.environ, 'OPENAI_API_KEY': '', 'PYTHONPATH': str(root)}
    result = subprocess.run([str(root / '.venv/bin/python'), str(root / 'scripts/run_eval.py'), '--check-result', str(saved), '--faithfulness-min', '.75'], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_nan_threshold_cannot_disable_the_gate():
    scores = dict.fromkeys(METRICS, .8)
    assert 'threshold must be finite' in failures(scores, [scores], {'faithfulness': float('nan')})[0]
