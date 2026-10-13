from unittest.mock import patch
import pytest
from src.config import settings
from src.evaluation import build_eval_dataset
from src.models import QueryResponse, Source, TokenUsage


def answer():
    return QueryResponse(answer="7.4 oz", sources=[Source(doc_id="p1", chunk_text="Weight: 7.4 oz", similarity_score=.9)], confidence=.9, model="gpt-4o", tokens=TokenUsage(prompt_tokens=10, completion_tokens=3), cost_usd=.001)


def test_interrupted_dataset_resumes_only_missing_answers_and_separates_depths(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "eval_dataset_cache_dir", str(tmp_path))
    golden = [{"question": question, "ground_truth": "7.4 oz", "contexts": []} for question in ("Q1", "Q2")]
    with patch("src.evaluation.run_eval.run_pipeline", side_effect=[answer(), RuntimeError("interrupted")]):
        with pytest.raises(RuntimeError, match="interrupted"):
            build_eval_dataset(golden, top_k=5)
    with patch("src.evaluation.run_eval.run_pipeline", return_value=answer()) as run:
        dataset = build_eval_dataset(golden, top_k=5)
        run.assert_called_once_with("Q2", top_k=5)
        assert len(dataset) == 2
    with patch("src.evaluation.run_eval.run_pipeline", return_value=answer()) as run:
        build_eval_dataset(golden, top_k=3)
        assert run.call_count == 2
