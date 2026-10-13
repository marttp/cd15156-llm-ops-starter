"""Request correlation and billable-operation recording shared across layers."""

import json
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from functools import wraps
from opentelemetry import trace

from src.config import settings
from src.models import TokenUsage

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_log_lock = Lock()


def operation_span(name):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            with trace.get_tracer(fn.__module__).start_as_current_span(name):
                return fn(*args, **kwargs)
        return wrapped
    return decorate


def record_operation(model: str, usage: TokenUsage, cost_usd: float, query_type: str, *, path=None) -> dict:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id.get(),
        "operation": {"simple": "generation", "complex": "generation", "hallucination_check": "judge"}.get(query_type, query_type),
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "cost_usd": cost_usd,
        "query_type": query_type,
    }
    log_path = Path(path or settings.cost_log_path)
    with _log_lock:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
    return record
