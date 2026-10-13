from unittest.mock import MagicMock, patch
from src.cache.semantic import cache_namespace, lookup


def test_retrieval_depth_has_a_distinct_cache_namespace():
    assert cache_namespace(3) != cache_namespace(5)


def test_legacy_or_mismatched_cache_entries_are_misses():
    col = MagicMock()
    col.count.return_value = 1
    col.query.return_value = {"ids": [["old"]], "distances": [[.01]], "metadatas": [[{"namespace": "obsolete"}]]}
    with patch("src.cache.semantic._collection", return_value=col), patch("src.cache.semantic.embed_query", return_value=[.1]):
        assert lookup("same question") is None
