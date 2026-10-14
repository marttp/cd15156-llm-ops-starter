"""Retry missing RAGAS score cells using the original answer/context, never invented scores."""

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.run_config import RunConfig
from src.evaluation.run_eval import DEFAULT_METRICS, _build_llm, _build_embeddings
from src.evaluation.gates import METRICS, failures, statistics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result', type=Path)
    args = parser.parse_args()
    payload = json.loads(args.result.read_text())
    backup = args.result.with_name(args.result.stem + '-before-retry.json')
    if not backup.exists():
        backup.write_text(args.result.read_text())
    retried = payload.setdefault('score_retries', [])
    for index, row in enumerate(payload['rows']):
        for metric in METRICS:
            value = row.get(metric)
            if isinstance(value, (int, float)) and math.isfinite(value):
                continue
            print('Retrying', index, metric, row.get('user_input'), flush=True)
            dataset = Dataset.from_dict({
                'question': [row.get('user_input', row.get('question'))],
                'answer': [row.get('response', row.get('answer'))],
                'contexts': [row.get('retrieved_contexts', row.get('contexts'))],
                'ground_truth': [row.get('reference', row.get('ground_truth'))],
            })
            selected = next(m for m in DEFAULT_METRICS if m.name == metric)
            result = evaluate(dataset, metrics=[selected], llm=_build_llm(), embeddings=_build_embeddings(), run_config=RunConfig(max_workers=1, timeout=300, max_retries=2))
            score = float(result.to_pandas().iloc[0][metric])
            if not math.isfinite(score):
                raise RuntimeError(f'{metric} remains incomplete; refusing to accept the artifact')
            row[metric] = score
            retried.append({'row': index, 'metric': metric, 'question': row.get('user_input'), 'score': score, 'utc': datetime.now(timezone.utc).isoformat(), 'method': 'Same saved answer/context; fresh serialized metric judgment'})
    frame = pd.DataFrame(payload['rows'])
    payload['aggregate'] = {m: float(frame[m].mean()) for m in METRICS}
    payload['statistics'] = statistics(payload['rows'])
    errors = failures(payload['aggregate'], payload['rows'])
    if errors:
        raise RuntimeError('; '.join(errors))
    args.result.write_text(json.dumps(payload, indent=2, allow_nan=False))
    print('Complete aggregate:', payload['aggregate'], flush=True)


if __name__ == '__main__':
    main()
