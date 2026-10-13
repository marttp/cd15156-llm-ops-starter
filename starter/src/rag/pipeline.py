"""End-to-end RAG flow: retrieve -> prompt -> generate -> respond."""

from src.config import settings
from src.models import QueryResponse
from src.rag.generator import generate
from src.rag.retriever import retrieve
from opentelemetry import trace


def run_pipeline(
    question: str, model: str | None = None, top_k: int = settings.retrieval_top_k
) -> QueryResponse:
    """Run the full RAG pipeline and return a structured QueryResponse."""
    chosen_model = model or settings.model_complex
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("retrieval") as span:
        sources = retrieve(question, top_k=top_k)
        span.set_attribute("retrieval.source_count", len(sources))
    with tracer.start_as_current_span("generation") as span:
        answer, usage, cost = generate(question, sources, chosen_model)
        span.set_attribute("llm.model_name", chosen_model)
        span.set_attribute("llm.token_count.prompt", usage.prompt_tokens)
        span.set_attribute("llm.token_count.completion", usage.completion_tokens)
    confidence = (
        sum(s.similarity_score for s in sources) / len(sources) if sources else 0.0
    )
    return QueryResponse(
        answer=answer,
        sources=sources,
        confidence=confidence,
        model=chosen_model,
        tokens=usage,
        cost_usd=cost,
    )
