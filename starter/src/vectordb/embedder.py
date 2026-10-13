"""Thin wrapper around OpenAI's embeddings API."""

from openai import OpenAI

from src.config import settings
from src.models import TokenUsage
from src.pricing import compute_cost
from src.telemetry import record_operation

_client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url or None,
    timeout=settings.provider_timeout_s,
    max_retries=settings.provider_max_retries,
)


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts and return their vector representations."""
    response = _client.embeddings.create(
        input=texts, model=settings.embedding_model
    )
    usage = TokenUsage(prompt_tokens=response.usage.prompt_tokens, completion_tokens=0)
    record_operation(settings.embedding_model, usage, compute_cost(settings.embedding_model, usage), "embedding")
    return [item.embedding for item in response.data]


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed([text])[0]
