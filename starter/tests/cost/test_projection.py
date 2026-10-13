import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("projection", Path(__file__).resolve().parents[2] / "scripts/project_costs.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_projection_counts_http_requests_and_excludes_catalog_bootstrap():
    records = [
        {"request_id": None, "cost_usd": 5},
        {"request_id": "one", "cost_usd": .01, "operation": "generation", "model": "gpt-4o"},
        {"request_id": "one", "cost_usd": .001, "operation": "judge", "model": "gpt-4o-mini"},
    ]
    report = module.project(records, 2, daily_requests=10000)
    assert report["cost_per_http_request_usd"] == pytest.approx(.0055)
    assert report["projected_daily_api_cost_usd"] == pytest.approx(55)
    assert report["generation_tier_counts"] == {"gpt-4o": 1}
