# ThirdShotHub operating notes

## Runtime

Run all commands from `starter/`. Python 3.12 and the tracked uv lock define the environment. `make setup` installs locally; `make load-data` embeds thirty static catalog products. The API's lifespan owns the inbox observer. Use `make serve` locally and `make serve-proxy` only in the course proxy workspace. Phoenix is local; AWS resources are not required by this deployment.

`/health` is liveness only; it does not prove provider access or a populated corpus. Live query checks establish those outcomes.

For local access bind Phoenix to `127.0.0.1`. Store Vocareum credentials only in the ignored `.env`; its endpoint is `https://openai.vocareum.com/v1`. The sample key is not a working credential. Keep configuration changes out of committed evidence. Restart the API after changing environment settings.

## API contracts

`POST /query` accepts a question of 1–4000 characters and retrieval depth of 1–20. FastAPI executes synchronous scanner and provider work in its bounded thread pool. SDK calls have a 45-second timeout and at most two retries, using the SDK's transient-error/backoff policy. Generation is capped at 768 output tokens by default; classification and judging are capped at 256. These are process-level defaults and can be tightened in local settings.

Injection is checked before model or embedding calls. PII is redacted before cache lookup, classification, retrieval and generation. `blocked_by` identifies a safety rejection or, for compatibility with the course schema, a PII-redaction annotation. A `pii_redacted` response can still contain a valid answer. Confidence is mean retrieval similarity, not a probability of correctness.

A missing source set, unsupported answer, invalid judge verdict or unavailable judge produces a safe refusal. Judge failure therefore reduces availability. Generation token/cost metadata remains attached to filtered answers because the call was already billed. Authentication/status errors are reported as stable 502 errors; provider timeouts/connectivity and rate limits return 503. Optional cache failures degrade to retrieval or return an already checked answer.

`tokens` and `cost_usd` describe answer generation only. A cache hit has zero new generation tokens/cost, but its embedding lookup is still billable. The JSONL operation log records that overhead separately and correlates operations with a fresh request identity. Phoenix trace IDs refer to the current request, including cache hits.

## Ingestion and cache

Inbox JSONs need the eight required fields, nonempty bounded strings, a safe product ID, a finite nonnegative price and nonempty specifications. Files are size-limited to 256 KiB. The watcher debounces partial writes, chunks and embeds valid products, upserts by ID, and clears cached answers. Invalid inputs move to `data/inbox/failed/` with a sibling `.error.txt`. Successful fixture files remain available as the audit trail.

Upserts replace the single product chunk without multiplying duplicate IDs. If chunking changes to multiple chunks, introduce unique chunk IDs and explicit obsolete-chunk deletion first. Bulk reload does not delete catalog products removed from disk. Rebuild a versioned index for deletion or embedding-model migration rather than silently mixing vectors.

Cache namespaces include prompt content, model names and retrieval depth. Entry TTL is enforced on lookup. The threshold benchmark records hit counts and a wrong-product probe; configure the deployment threshold from those measurements. Do not assume any finite set of cache probes proves universal semantic correctness.

## Quality and cost gates

Run the complete four-metric RAGAS suite against the versioned golden set. Save row-level results, descriptive statistics and the k=3,5,10 comparison. Missing/non-finite metrics fail verification. A named quality floor is checked against saved results without paid calls. On violation, withhold the new prompt/index, examine the failing questions and retrieved chunks, and reevaluate the corrected candidate before release.

For interruptible runs, set `EVAL_DATASET_CACHE_DIR` to a private local checkpoint directory. Completed generated answers are reused only for the same golden-set, catalog, prompt, model, output cap and retrieval-depth fingerprint. Sweep and independent evaluation use separate directories so the final evaluation remains an independent generation run. Metric judgments themselves must finish before a score artifact is accepted.

Cost reports distinguish operation totals from generation-tier query counts. Dollar amounts use published uncached token rates, not an independently verified Vocareum invoice. Cached-input discounts and provider billing for responses lost during retries are not reconstructed. Routing savings compare the same generation token counts against a named complex-model rate; they are estimates, not an observed alternate-model bill. Keep classifier, judge and embedding overhead visible. Daily projections assume unchanged traffic mix and token lengths and exclude evaluation, hosting and bootstrap costs.

## Deployment limits

This is a reproducible single-process capstone service. It has no authentication gateway, distributed quota, multi-tenant isolation, replicated database or availability SLO. The SSE endpoint buffers tokens until full-answer output checks pass. Its framing is compatible with streaming clients, but it gives up early display to avoid emitting an answer before grounding checks. The raw TTFT benchmark measures the generator separately and cannot be treated as guarded endpoint latency. These limits do not replace any of the nine required rubric proofs.
