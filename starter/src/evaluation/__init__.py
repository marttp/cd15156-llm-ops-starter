"""Evaluation exports are lazy so saved-score gates need no model client."""

from importlib import import_module

__all__ = ["DEFAULT_METRICS", "load_golden_set", "build_eval_dataset", "evaluate_pipeline", "summarize"]


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(name)
    return getattr(import_module("src.evaluation.run_eval"), name)
