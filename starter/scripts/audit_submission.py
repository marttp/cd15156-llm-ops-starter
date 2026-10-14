"""Check the nine rubric evidence rows without model calls or credentials."""

import hashlib
import ast
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ('faithfulness', 'answer_relevancy', 'context_recall', 'context_precision')


def read(relative):
    return (ROOT / relative).read_text()


def load(relative):
    return json.loads(read(relative))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def finite_scores(payload):
    require(len(payload['rows']) == 35, 'Full 35-question corpus required')
    for row in [payload['aggregate']] + payload['rows']:
        require(all(isinstance(row.get(metric), (int, float)) and math.isfinite(row[metric]) for metric in METRICS), 'Incomplete metric scores')


def main():
    products = [load('data/products/' + path.name) for path in (ROOT / 'data/products').glob('demo_*.json')]
    require(len(products) >= 5, 'Need five new products')
    ids = {p['product_id'] for p in products}
    curl = load('evidence/live/structured-curl.json')
    require(ids & {s['doc_id'] for s in curl['sources']}, 'New product retrieval missing')
    print('PASS 1: five catalog additions and literal curl retrieval')

    require({'answer', 'sources', 'confidence', 'model', 'tokens', 'cost_usd', 'cached', 'trace_id', 'blocked_by'} <= curl.keys(), 'Response schema incomplete')
    require({'doc_id', 'chunk_text', 'similarity_score'} <= curl['sources'][0].keys(), 'Source schema incomplete')
    for k in (3, 5, 10):
        finite_scores(load(f'evidence/evaluation/sweep/top_k_{k}.json'))
    recommendation = load('evidence/evaluation/recommendation.json')
    require(recommendation['top_k'] in (3, 5, 10) and len(recommendation['deltas']) >= 2, 'Measured retrieval recommendation missing')
    print('PASS 2: complete response, twelve sweep values and justified retrieval depth')

    routing = [load(f'evidence/live/routing-{i}.json') for i in (1, 2, 3)]
    require(len({r['response']['model'] for r in routing}) >= 2, 'Routing does not vary model')
    require({'simple', 'complex'} <= {r['classification'] for r in routing}, 'Routing classifications incomplete')
    print('PASS 3: simple and complex classifications across configured model tiers')

    for i in (1, 2, 3):
        product = load(f'data/inbox/evidence_valid_{i}.json')
        require(product['product_id'] in {s['doc_id'] for s in load(f'evidence/live/ingestion-{i}.json')['response']['sources']}, 'Live ingestion source missing')
    require('demo_inbox_towel_1' in {s['doc_id'] for s in load('evidence/live/ingestion-curl.json')['sources']}, 'Inbox curl missing')
    require('invalid JSON' in read('data/inbox/failed/evidence_malformed.json.error.txt'), 'Quarantine reason missing')
    require('Ingested demo_inbox_towel_3' in read('evidence/live/ingestion-runtime.log'), 'Running observer evidence missing')
    print('PASS 4: three live ingests, source-linked curl and quarantine')

    evaluation = load('evidence/evaluation/final.json')
    finite_scores(evaluation)
    require(evaluation['aggregate']['faithfulness'] >= .90, 'Faithfulness release floor violated')
    require('python exit=0' in read('evidence/evaluation/gate-pass.txt') and 'python exit=2' in read('evidence/evaluation/gate-fail.txt'), 'Regression gate demonstrations missing')
    print('PASS 5: complete independent evaluation and demonstrated quality gate')

    tree = ast.parse(read('src/guardrails/input_guards.py'))
    patterns = next(node.value.elts for node in tree.body if isinstance(node, ast.AnnAssign) and getattr(node.target, 'id', None) == 'INJECTION_PATTERNS')
    for i in (1, 2, 3):
        expected = 'prompt_injection: matched pattern ' + repr(patterns[i - 1].args[0].value)
        require(load(f'evidence/live/guard-{i}-blocked.json')['response']['blocked_by'] == expected, 'Wrong injection pattern in evidence')
        require(load(f'evidence/live/guard-{i}-legitimate.json')['response']['blocked_by'] is None, 'Legitimate query blocked')
    calibration = load('evidence/live/output-judge-calibration.json')
    require(calibration['positive_count'] >= 6 and calibration['negative_count'] >= 6 and calibration['false_positive_rate'] == 0 and calibration['true_positive_rate'] == 1, 'Output guard calibration failed')
    safety = load('evidence/live/supplemental-safety.json')
    feature = next(r for r in safety['rows'] if r['kind'] == 'unsupported_feature')
    require(feature['response']['blocked_by'] and feature['response']['blocked_by'].startswith('hallucination:'), 'Unsupported negative feature claim not blocked')
    print('PASS 6: three paired new-pattern HTTP demonstrations and output safety calibration')

    trace_requests = load('evidence/live/trace-refresh-queries.json')
    require(len(trace_requests) >= 10, 'Need ten traced HTTP requests')
    traces = read('evidence/live/traces.md')
    require(all(name in traces for name in ('classification', 'retrieval', 'generation')), 'Required trace operations missing')
    require(any(r['response']['trace_id'] in traces for r in trace_requests), 'Trace export does not match HTTP responses')
    print('PASS 7: ten requests and matching labeled Phoenix operation traces')

    log = read('data/cost_log.jsonl')
    require(log == read('evidence/live/cost_log.jsonl') and len(log.splitlines()) >= 50, 'Cost snapshots do not match')
    require((ROOT / 'evidence/live/cost-dashboard.png').stat().st_size > 1000, 'Rendered dashboard missing')
    require(all(label in read('evidence/live/cost-report.txt') for label in ('Baseline (gpt-4o)', 'Savings:', 'Per-tier summary:')), 'Savings report incomplete')
    print('PASS 8: real same-log cost evidence, dashboard and named baseline savings')

    writeup = read('WRITEUP.md')
    headings = re.findall(r'^## Deliverable (\d+)\b', writeup, re.MULTILINE)
    require(headings == [str(i) for i in range(1, 10)], 'Nine ordered writeup sections required')
    require(not re.search(r'TODO|\?\.\?\?\?|paste here', writeup, re.IGNORECASE), 'Unfinished writeup placeholder')
    counts = re.findall(r'(\d+) passed', read('evidence/final-tests.txt'))
    require(counts and int(counts[-1]) >= 195, 'Required tests not demonstrated')
    require('Automated: 4 passed, 0 failed' in read('evidence/final-verify.txt'), 'Verification output incomplete')
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT.parent, text=True).splitlines()
    require('starter/.env' not in tracked, 'Secret environment file tracked')
    for relative in tracked:
        path = ROOT.parent / relative
        if path.is_file() and path.suffix not in {'.png', '.jpg'}:
            require(not re.search(r'(?<![A-Za-z0-9])(?:voc-[A-Za-z0-9_.-]{25,}|sk-[A-Za-z0-9_-]{25,}|AKIA[A-Z0-9]{16})', path.read_text(errors='ignore')), 'Credential-shaped value in ' + relative)
    manifest = load('evidence/live/manifest.json')
    for relative, digest in manifest['files'].items():
        require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, 'Source artifact drift: ' + relative)
    print('PASS 9: ordered writeup, test/verify evidence, source provenance and secret-free repository')
    print('Rubric evidence audit: 9 passed, 0 failed')


if __name__ == '__main__':
    main()
