"""HTTP API: POST /query, GET /health.

The ``/query`` handler composes the full LLM Ops stack the course teaches:
input guards (regex-based prompt-injection detection + PII redaction),
semantic cache lookup against the redacted question, the tiered model
router, and output guards (hallucination + off-topic). Cleaned questions
are cached only after passing the output guards. Blocked or filtered
requests return a safe ``QueryResponse`` with ``blocked_by`` set.

Layer-by-layer alternates (``guarded_route_query``, ``cached_route_query``,
the LLM-Guard variant) remain available as standalone wrappers for tests
and for module-by-module exploration in the curriculum.
"""

from fastapi import APIRouter, HTTPException
from functools import wraps
from uuid import uuid4
from opentelemetry import trace
from src.telemetry import request_id
from src.config import settings
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field

from src.cache.semantic import lookup as cache_lookup
from src.cache.semantic import store as cache_store
from src.gateway.router import route_query
from src.guardrails.llm_guard.input_guards import detect_pii, detect_prompt_injection
from src.guardrails.llm_judge.output_guards import check_hallucination, is_off_topic
from src.guardrails.wrapper import (
    SAFE_BLOCKED_MESSAGE,
    SAFE_FILTERED_MESSAGE,
    _safe_response,
)
from src.models import QueryResponse

router = APIRouter()


class QueryRequest(BaseModel):
    """Customer-facing FAQ request body.

    ``question`` is capped at 4000 characters as a cheap LLM04 (model DoS)
    mitigation: real FAQ questions never approach this size, and Pydantic
    rejects the request with HTTP 422 before any LLM or embedding call.
    ``top_k`` is bounded so a single request can't pull a runaway number
    of chunks out of Chroma.
    """

    question: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(settings.retrieval_top_k, ge=1, le=20)


def _annotate_pii(response: QueryResponse, pii_found: list[str]) -> QueryResponse:
    """Tag a non-blocked response with which PII categories were redacted.

    The response itself is unchanged; only ``blocked_by`` becomes a
    descriptive marker (``pii_redacted: email,phone``) so callers can
    surface a notice without having to re-scan the answer.
    """
    if not pii_found:
        return response
    return response.model_copy(
        update={"blocked_by": f"pii_redacted: {','.join(pii_found)}"}
    )


def trace_request(fn):
    @wraps(fn)
    def wrapped(request):
        token = request_id.set(uuid4().hex)
        try:
            with trace.get_tracer(__name__).start_as_current_span("faq_request") as span:
                span.set_attribute("request.id", request_id.get())
                result = fn(request)
                ctx = span.get_span_context()
                current_id = format(ctx.trace_id, "032x") if ctx.is_valid else None
                span.set_attribute("request.cached", result.cached)
                span.set_attribute("rag.model", result.model)
                return result.model_copy(update={"trace_id": current_id})
        finally:
            request_id.reset(token)
    return wrapped


@router.post("/query", response_model=QueryResponse)
@trace_request
def query(request: QueryRequest) -> QueryResponse:
    """Run the full guarded + cached + traced FAQ pipeline.

    The handler intentionally inlines the layer composition rather than
    delegating to a single wrapper, because seeing the order of layers at
    the HTTP boundary is part of the lesson:

    1. ``detect_prompt_injection`` — short-circuits to a safe response on
       match. The LLM is never called for blocked input.
    2. ``detect_pii`` — redacts emails, phone numbers, SSNs, credit cards.
       The redacted text is what flows downstream; raw PII never reaches
       the cache, the LLM, or the tracing backend.
    3. ``cache_lookup`` — returns a cached ``QueryResponse`` if the
       embedding is within the similarity threshold of a prior query.
    4. ``route_query`` — classify simple/complex, dispatch to the right
       model, run the traced RAG pipeline, log per-request cost.
    5. ``check_hallucination`` and ``is_off_topic`` — output guards that
       block answers citing nonexistent products or veering off-topic.
       A flagged response is **not** cached.
    6. ``cache_store`` — persist the (cleaned-question, response) pair
       only after the output guards pass.

    Standalone wrappers (``guarded_route_query`` in ``src.guardrails`` and
    ``cached_route_query`` in ``src.cache``) compose the same pieces in
    isolation; they remain for tests and module-by-module exploration.
    """
    if reason := detect_prompt_injection(request.question):
        return _safe_response(SAFE_BLOCKED_MESSAGE, blocked_by=reason)
    cleaned, pii_found = detect_pii(request.question)

    if settings.semantic_cache_enabled:
        if cached := cache_lookup(cleaned, top_k=request.top_k, threshold=settings.semantic_cache_threshold):
            return _annotate_pii(cached, pii_found)

    try:
        response = route_query(cleaned, top_k=request.top_k)
    except (APITimeoutError, APIConnectionError) as exc:
        raise HTTPException(status_code=503, detail="model_provider_unavailable") from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=503, detail="model_provider_rate_limited", headers={"Retry-After": "10"}) from exc
    except APIStatusError as exc:
        raise HTTPException(status_code=502, detail="model_provider_error") from exc

    if not response.sources:
        return response.model_copy(update={"answer": SAFE_FILTERED_MESSAGE, "confidence": 0.0, "blocked_by": "retrieval: no_sources"})
    if reason := check_hallucination(response.answer, response.sources):
        return response.model_copy(update={"answer": SAFE_FILTERED_MESSAGE, "sources": [], "confidence": 0.0, "blocked_by": reason})
    if reason := is_off_topic(response.answer):
        return response.model_copy(update={"answer": SAFE_FILTERED_MESSAGE, "sources": [], "confidence": 0.0, "blocked_by": reason})

    if settings.semantic_cache_enabled:
        cache_store(cleaned, response, top_k=request.top_k)
    return _annotate_pii(response, pii_found)


@router.get("/health")
async def health() -> dict:
    """Liveness probe. Returns 200 with no dependency checks.

    Intentionally cheap so a load balancer can hit it frequently. Does
    *not* verify Chroma or OpenAI connectivity — those are observed via
    the cost log and Phoenix traces, not at this seam.
    """
    return {"status": "ok"}
