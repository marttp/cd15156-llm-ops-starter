# Evidence status and reproduction

The baseline and phase test transcripts are observed local results using Python 3.12. External services are mocked by the supplied test fixtures. Input guard calibration uses the actual locally downloaded ML scanners, but it is not HTTP rubric evidence.

Live provider evidence has not been captured. No rubric row is claimed complete until the final audit links all required artifacts and the writeup contains their analysis.

## Capture workflow

Run from `starter/` after configuring the ignored `.env` with a funded Vocareum key and endpoint. The sample README key is not usable credentials.

1. `make setup`, then `make load-data`.
2. `SEMANTIC_CACHE_ENABLED=false PHOENIX_HOST=127.0.0.1 make serve`.
3. In a second terminal, `PYTHONPATH=. uv run --no-project python scripts/capture_live_evidence.py`.
4. `make show-traces > evidence/live/traces.md`. Preserve a trace with all three required named operations and compute its slowest fraction against the full HTTP request span.
5. Capture the rendered `http://localhost:8080/cost-dashboard` as `evidence/live/cost-dashboard.png` while the same cost log is active. A saved HTML page alone does not satisfy the screenshot requirement.
6. `make eval-topk-sweep`. All per-row files and the comparison table are saved under `evidence/evaluation/sweep/`.
7. Select retrieval depth from measured deltas and apply `RETRIEVAL_TOP_K` in local configuration. Restart the service when changing process-level settings.
8. `PYTHONPATH=. uv run --no-project python scripts/run_eval.py --max-workers=1 --top-k=<selected> --output=evidence/evaluation/final.json`.
9. Derive a named threshold from observed statistics. Validate the saved result with `--check-result` and that threshold, then demonstrate a forced failure with a stricter floor. Save both exit outcomes.
10. Assemble `WRITEUP.md`, capture final `make test` and `make verify`, then audit all nine rows and scan tracked content for secrets.

The capture script preserves the complete actual cost log in `evidence/live/cost_log.jsonl`, the same entries used by the dashboard and report. Generation, classification, judge and embedding records are distinct. Per-model operation count is not customer-query count. Routing savings are a token-matched generation estimate using the course pricing table, not an observed alternate-provider bill. Evaluation judge spend is outside the API workload report.

For a repository-only submission, restore the tracked snapshot to the rubric path with `cp evidence/live/cost_log.jsonl data/cost_log.jsonl`. Retain quarantine fixture sources and captured path/error text because `data/inbox/failed/` is ignored. Do not commit `.env`, Chroma databases, Phoenix databases or raw personal inputs.

## Optional measurements

Stop the API before `PYTHONPATH=. uv run --no-project python scripts/measure_cache.py` so one process owns Chroma. The benchmark runs the guarded query function, sweeps 0.85/0.90/0.95, records six paraphrases and checks a wrong-product weight probe. It saves actual hit counts and collection metadata, and fails if no threshold yields at least three hits. Select the deployed threshold from the observed false-positive and hit-rate results.

After the HTTP workload capture, `PYTHONPATH=. uv run --no-project python scripts/project_costs.py` projects that workload at 10,000 HTTP queries/day. Bootstrap costs are excluded explicitly; classification, embeddings, generation and judging for those requests remain included. Discuss provider rate limits, cache pressure, evaluation cadence and daily spend ceilings in the writeup.
