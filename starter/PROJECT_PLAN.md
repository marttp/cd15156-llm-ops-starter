# LLMOps final project plan

Planning baseline: 2026-10-14, starter commit `1290dd1f9a054a6ec8692032e7d06d942a76d833`.
Fork: https://github.com/marttp/cd15156-llm-ops-starter
Upstream: https://github.com/udacity/cd15156-llm-ops-starter

Status: fork created and local remotes configured. Implementation and live evidence have not started. No rubric row is marked passed.

## Scope and completion rule

Extend the supplied ThirdShotHub application under `starter/`. Preserve its course package boundaries, required interfaces, tests, and toolchain. Use `INSTRUCTIONS.md`, `rubric.md`, and `TROUBLESHOOTING.md` as the assignment contract; use the adjacent LLMOps exercises for mechanisms and verification patterns. The exercises use ScikitDocs and different module interfaces, so adapt their ideas to product JSONs rather than copying implementations blindly.

Every rubric row needs working behavior, captured evidence, and an explanation in `starter/WRITEUP.md`. Passing mocked tests or `make verify` alone does not establish live completion. Submission root is `starter/`, where the assignment files and Makefile live; the repository README must make that location obvious.

The project description mentions multiple providers, but the nine rubric rows require model tiers, not two providers. The required path retains the course's OpenAI tier mapping. A live second provider is a separately identified extension requiring credentials and its own evaluation; a stub is not evidence of multi-provider operation.

## Backend design decisions

- Keep FastAPI, embedded Chroma, Phoenix, Jinja2, RAGAS, LLM Guard and the LLM judge. A separate database server or container stack adds work without satisfying another rubric row.
- Keep the ingestion observer in the API lifespan. The starter documents stale in-memory Chroma indexes when a separate watcher writes to the same persistent store.
- Give each HTTP request a fresh request/trace identity. Time classification, retrieval, generation and output validation around their actual work, under the same request trace. Cache hits must not reuse the original request's trace identity.
- Preserve `QueryResponse` fields and explain their semantics. Current confidence is average retrieval similarity, not a calibrated probability that the answer is correct. Safe refusals legitimately have no sources.
- Bound provider timeouts, retry attempts, completion tokens and request concurrency. Retry transient failures only, with backoff; account for existing SDK retries so retry layers do not multiply attempts. Authentication failures, invalid inputs and exhausted budget must not trigger retry loops.
- Handle upstream failures with stable API errors. Record consumed tokens even if an answer is later filtered. Distinguish a safety block from a PII redaction annotation while retaining the rubric's `blocked_by` contract.
- Track generation, classification, embedding and judge spend separately. Distinguish HTTP request counts from billable operation counts. Explain whether `cost_usd` means generation cost or total request cost.
- Use a fixed, versioned evaluation corpus and prompts. Persist row-level scores, model/configuration metadata and finite aggregate metrics. Missing or NaN metrics are incomplete evidence.
- Invalidate or version semantic cache entries on corpus/prompt changes and include retrieval configuration in cache eligibility. Measure false matches across products. PII must be removed before prompts, traces, logs and cache storage.
- Validate ingestion field types and values, retain unique product/chunk IDs, test duplicate delivery and product replacement, and preserve quarantine reasons. Keep fixture source files outside ignored runtime directories so ingestion can be reproduced.

## Work sequence

### Phase 1: establish the baseline

Read the assignment files and exercise modules listed below. Provision Python 3.12 as selected by `.python-version`, use `make setup`, and preserve resolved dependencies for a fresh clone. Create local configuration without overwriting existing secrets. Run the unchanged tests and verification before extensions, recording the actual counts and any environment failures.

Inspect `tests/integration/test_dependency_graph.py` before adding cross-package imports. Retain the starter's forward-dependency rule. Create focused implementation commits after each verified phase.

Exit gate: environment reproducible, baseline checks captured, local provider configuration available for live runs. No guessed runtime or API budget estimate is a completion claim.

### Phase 2: catalog and live ingestion

Add five distinct, clearly documented demo products under `data/products/`, covering useful category and attribute differences. They are course fixtures, not verified claims about real commercial products. Validate and load them with the existing loader. Extend golden questions to cover new products, comparisons and unavailable features.

Use three additional products as inbox fixtures. Start `make serve`, drop all three while its in-process observer is running, and record ingestion plus query evidence without restarting or manually reloading. Drop malformed JSON and capture its failed path and sibling `.error.txt`. Add behavioral checks for invalid field types, duplicate deliveries, partial writes and replacement semantics where changed.

Exit gate: all five static additions validate, retrieval cites a new ID, three live ingests are demonstrated, and malformed input is quarantined.

### Phase 3: request contracts, routing and safety

Preserve the simple/complex gateway and configured model tiers. Capture at least three uncached queries spanning a single fact, a comparison and a more demanding recommendation, with actual classification and model selection. Cache must not hide routing during this measurement.

Add three narrow injection patterns to `src/guardrails/input_guards.py`, covering attacks absent from the baseline. Capture one blocked API response and one legitimate response with `blocked_by: null` for each. Test the live layered guard path, not only the regex helper. Avoid brand-name PII false positives in the paired legitimate fixtures; correct measured domain false positives without disabling general PII protection.

Probe accidental PII, off-topic input, unsupported features and malicious retrieved text. Calibrate the judge against grounded and fabricated claims. Treat unknown judge verdicts and judge unavailability explicitly; the current implementation fails open. For this service, choose a safe refusal on unverifiable output and document the availability tradeoff.

Add bounded provider calls and API failure behavior from the backend design decisions. Keep blocked-response and streaming contracts valid when adding successful-answer validation.

Exit gate: complete structured response captured, routing demonstrably varies by tier, six paired guardrail outputs captured, and affected failure cases pass behavioral checks.

### Phase 4: accurate tracing and cost records

Correct trace boundaries before collecting final measurements. Classification currently happens before `traced_pipeline`; the `rag_generation` child span is created after generation and cannot represent generation latency. Wrap the actual operations and capture at least ten live HTTP requests. Ensure one uncached trace has labeled classification, retrieval and generation spans. Export via `make show-traces` or capture Phoenix in `llm-ops-capstone`. Compute slowest-step duration divided by full request duration, with both raw durations stated.

Extend accounting where needed. Classifier and embeddings are not recorded in the current request cost log; judge calls with unparseable responses also escape accounting. Maintain compatible report/dashboard readers when introducing operation metadata.

Generate at least fifty real billable log entries through the service using a controlled mix of uncached requests. Retain the HTTP request count separately because generation and judge can each create a log entry. Do not use `make seed-cost-log` synthetic rows as measured savings evidence. Capture five sanitized log lines, per-tier counts and average cost, `make cost-report`, and a rendered `/cost-dashboard` screenshot from the same log.

Report a generation-only counterfactual against the named complex model using identical recorded token counts, and separately report total operational spend. This avoids describing classifier/judge calls as customer queries or claiming a token-matched counterfactual is a measured second-model experiment.

Exit gate: trace timings are meaningful, cost log has at least fifty real entries, dashboard and report agree, and all evidence uses the same recorded run.

### Phase 5: measured quality and regression gate

Freeze the catalog, prompt version and golden set. Run `make eval-topk-sweep` at 3, 5 and 10, retaining all four metrics and row-level artifacts where possible. Select `top_k` using measured quality, latency and prompt size, citing at least two numeric per-metric deltas. Apply the selected depth consistently to the service default and evaluation; the starter has defaults in multiple functions.

Run a separate `make eval` at the chosen configuration and save per-row results. Name the lowest metric and examine concrete failing questions, retrieved chunks and generated claims to justify its cause. Derive a named threshold from an observed median, percentile or range. Implement a gate that exits nonzero on regression or missing/non-finite metrics, and demonstrate a passing and forced-failing check. State the release action on violation, such as withholding the new prompt/index until investigation and reevaluation.

Use the capstone's default `EVAL_MAX_WORKERS=1` initially. Exercise documentation has different concurrency defaults and datasets; do not carry their sample scores or settings into this project as results.

Exit gate: twelve finite sweep cells, selected depth and two deltas, a complete independent eval, data-derived threshold and proven gate behavior.

### Phase 6: submission audit

Assemble `WRITEUP.md` with nine numbered sections in rubric order, each containing an implementation summary and its exact evidence. Store durable sanitized artifacts in a tracked `evidence/` directory. Runtime cost logs, inbox quarantine and harvester output are ignored by the starter, so provide a reproducible evidence bundle and document restoration to rubric paths; never silently assume ignored files reach GitHub. Retain the actual required cost log at `data/cost_log.jsonl` in the submitted working bundle or explicitly track a sanitized snapshot of that file for a repository-only submission.

Capture final `make test` output with at least 195 passing and `make verify` with zero failed. Audit every manual criterion separately. Scan committed content for secrets, ensure `.env` is absent, and verify setup from a fresh clone. Include configuration values without credentials and an artifact manifest with commit, prompt/catalog/golden-set versions and collection time.

Exit gate: all nine audit rows below have code paths, evidence references and observed outcomes. No TODOs, fabricated measurements or unqualified production claims remain.

## Rubric coverage matrix

| Row | Required implementation or operation | Required evidence | Course exercise reference |
| --- | --- | --- | --- |
| 1 | Add at least 5 schema-valid products; chunk, embed and load | Product filenames/IDs and `/query` response whose source ID matches an addition | Module 05 vector databases; module 24 RAGOps |
| 2 | Complete RAG response; tune retrieval depth | All response fields and source fields; four metrics at k=3,5,10; recommendation with at least 2 per-metric deltas | Module 07 RAG; module 11 evaluation |
| 3 | Preserve and verify configured tier routing | At least 3 query outputs including simple and complex; differing models; classification for each; sanitized tier config | Module 18 gateway |
| 4 | In-process live ingestion and quarantine | At least 3 valid inbox drops during service operation; retrieved new ID; malformed input path and `.error.txt` contents | Module 24 RAGOps |
| 5 | Full evaluation plus a data-derived regression policy | Four aggregate metrics from `make eval`; lowest-metric diagnosis; named threshold, observed statistic and action on violation | Module 11 evaluation; module 03 prompt versioning |
| 6 | Add at least 3 injection patterns; retain PII and output protection | Blocked and legitimate `blocked_by: null` API pair for each addition; supplemental PII/hallucination checks | Module 20 guardrails; module 07 grounding |
| 7 | Correct per-operation tracing; issue at least 10 HTTP queries | Phoenix screenshot or `make show-traces`; one trace with classification/retrieval/generation; slowest duration and fraction of request latency | Module 09 tracing |
| 8 | At least 50 real log entries; consistent report and dashboard | Five log lines; dashboard screenshot; each tier's count/mean cost; report with named baseline, absolute and percentage savings | Module 13 cost monitoring; module 18 gateway |
| 9 | Reproducible, secret-free submission | Nine ordered writeup sections; final test output >=195 passed; verify output 0 failed; clean-clone instructions and tracked evidence | Capstone instructions, rubric and writeup template |

All rows are currently pending live implementation/verification.

## Learning resources

Resources live beside this fork in `../cd15156-llm-ops-exercises/`:

- `module-03-prompt-versioning/prompt-versioning-starter/INSTRUCTIONS.md`: versioned templates and measured prompt changes.
- `module-05-vector-databases/vector-databases-starter/INSTRUCTIONS.md`: collection population, retrieval diagnostics and embedding compatibility.
- `module-07-rag-pipeline/rag-pipeline-starter/INSTRUCTIONS.md`: grounding battery, refusal and retrieval comparisons.
- `module-09-observability-tracing/observability-tracing-starter/INSTRUCTIONS.md`: inspect a trace, export evidence and add span attributes.
- `module-11-evaluation-ragas/evaluation-ragas-starter/INSTRUCTIONS.md`: golden-set coverage, top-k sweep, failure diagnosis and CI threshold gates.
- `module-13-cost-monitoring/cost-monitoring-starter/INSTRUCTIONS.md`: real-query accounting, alerts and pre-call token budgets.
- `module-18-gateway-fastapi/gateway-fastapi-starter/INSTRUCTIONS.md`: retries, tier routing and provider adapters. Its Anthropic example contains a stub and is not live-provider proof.
- `module-20-guardrails-impl/guardrails-impl-starter/INSTRUCTIONS.md`: layered guards, judge calibration, consumption caps and boundary validation.
- `module-24-ragops-pipeline/ragops-pipeline-starter/INSTRUCTIONS.md`: live ingestion, quarantine and index lifecycle.

## Optional work after all required evidence passes

Prioritize semantic-cache correctness and a projection at 10,000 queries/day. For cache evidence, test six paraphrases, demonstrate at least three hits, sweep thresholds 0.85/0.90/0.95, and include a false-match case. Separate cached response metadata from actual current-request spend.

Streaming follows only if its input/output guards match the normal endpoint; compare TTFT on at least three uncached questions. A third tier or real second provider follows only if measured quality/cost justifies it. Do not delay the nine required deliverables to expand infrastructure.

## Current prerequisites and limits

Provider credentials, funded quota and live model access have not been checked. No paid calls, dependency installation, tests, quality evaluation or service run occurred during planning. Course estimates of cost and runtime are inconsistent across files and are not a reliable budget promise. Use a small live calibration batch to estimate actual spend before the full sweep.

Rubric completeness can be demonstrated with evidence; a passing grade remains the reviewer's decision. This course service can be submission-ready without proving multi-replica operation, internet-facing security or a production availability target. Document those deployment limits plainly.

## Pull request delivery sequence

Each PR uses a dedicated `codex/llmops-NN-*` branch in the project worktree, a 100–200 word What/Why/Change description, appropriate tests and evidence, then push and merge after checks pass. User authorization covers these operations.

1. Baseline: Python 3.12 constraint, reproducible dependencies, CI, execution plan and baseline checks.
2. Catalog and ingestion: five products, inbox fixtures, schema validation and ingestion failure tests.
3. Gateway and safety: provider bounds, guard extensions, judge failure behavior and API contracts.
4. Tracing and cost: real operation spans, request correlation, accounting and cache correctness.
5. Evaluation: persisted sweep results, selected retrieval configuration and regression gate.
6. Submission: live API/ingestion/safety/trace/cost/quality evidence, writeup and full rubric audit.
7. Optional measurements: semantic cache and scale projection; streaming or another provider only after required completion and sufficient resources.

Live-dependent PRs remain incomplete until real provider runs succeed. AWS is not required for the local rubric stack.
