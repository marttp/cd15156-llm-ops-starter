from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from src.gateway.app import create_app
from src.models import QueryResponse, Source, TokenUsage
from src.telemetry import record_operation, request_id
from src.cost.tracker import load_log


def test_cache_hits_receive_distinct_current_request_traces():
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    cached = QueryResponse(answer="7.4 oz", sources=[Source(doc_id="p1", chunk_text="7.4 oz", similarity_score=.9)], confidence=.9, model="gpt-4o-mini", tokens=TokenUsage(prompt_tokens=0, completion_tokens=0), cost_usd=0, cached=True, trace_id="old")
    with patch("opentelemetry.trace.get_tracer", return_value=provider.get_tracer("test")), patch("src.gateway.routes.detect_prompt_injection", return_value=None), patch("src.gateway.routes.detect_pii", return_value=("clean", [])), patch("src.gateway.routes.cache_lookup", return_value=cached):
        client = TestClient(create_app())
        first = client.post("/query", json={"question": "question"}).json()
        second = client.post("/query", json={"question": "question"}).json()
    assert first["trace_id"] != second["trace_id"]
    assert first["trace_id"] != "old"
    assert len(exporter.get_finished_spans()) == 2
    assert request_id.get() is None


def test_concurrent_cost_records_remain_valid_and_correlated(tmp_path):
    path = tmp_path / "operations.jsonl"
    def record(index):
        token = request_id.set(str(index))
        try:
            record_operation("gpt-4o-mini", TokenUsage(prompt_tokens=10, completion_tokens=2), .001, "classification", path=path)
        finally:
            request_id.reset(token)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(record, range(50)))
    records = load_log(path)
    assert len(records) == 50
    assert len({r["request_id"] for r in records}) == 50
    assert all(r["operation"] == "classification" for r in records)
