"""Project observed API workload spend; exclude uncorrelated bootstrap operations."""

import argparse
import json
from pathlib import Path


def project(records, http_requests, daily_requests=10_000):
    if http_requests <= 0:
        raise ValueError("http_requests must be positive")
    api = [record for record in records if record.get("request_id")]
    observed_cost = sum(record["cost_usd"] for record in api)
    generations = [r for r in api if r.get("operation") == "generation"]
    counts = {}
    for record in generations:
        counts[record["model"]] = counts.get(record["model"], 0) + 1
    return {"observed_http_requests": http_requests, "observed_billable_operations": len(api), "generation_tier_counts": counts, "observed_api_cost_usd": observed_cost, "cost_per_http_request_usd": observed_cost / http_requests, "daily_requests": daily_requests, "projected_daily_api_cost_usd": observed_cost / http_requests * daily_requests, "projected_30_day_api_cost_usd": observed_cost / http_requests * daily_requests * 30, "assumptions": "Same traffic mix, model rates and token sizes; excludes evaluation, hosting and catalog bootstrap. Rejected requests are included in the HTTP denominator."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=Path("evidence/live/cost_log.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("evidence/live/manifest.json"))
    args = parser.parse_args()
    records = [json.loads(line) for line in args.log.read_text().splitlines()]
    manifest = json.loads(args.manifest.read_text())
    report = project(records, manifest["http_queries"])
    output = Path("evidence/live/scale-projection.json")
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
