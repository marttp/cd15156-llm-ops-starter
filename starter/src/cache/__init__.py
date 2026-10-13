"""Semantic cache (Chroma collection) — implements the Semantic Caching module."""

from src.cache.semantic import (
    COLLECTION_NAME,
    KEY_PREFIX,
    clear,
    ensure_index,
    lookup,
    store,
)
from src.models import QueryResponse


def cached_route_query(question: str, top_k: int = 5, *, threshold: float = 0.85, ttl_s: int = 3600) -> QueryResponse:
    """Load gateway composition only when requested, keeping ingestion acyclic."""
    from src.cache.wrapper import cached_route_query as run
    return run(question, top_k=top_k, threshold=threshold, ttl_s=ttl_s)

__all__ = [
    "COLLECTION_NAME",
    "KEY_PREFIX",
    "ensure_index",
    "lookup",
    "store",
    "clear",
    "cached_route_query",
]
