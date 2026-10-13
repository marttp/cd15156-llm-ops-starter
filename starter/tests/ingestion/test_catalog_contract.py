import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.ingestion.watcher import ingest_file, validate_product

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def product():
    return json.loads((ROOT / "data/products/demo_control_paddle.json").read_text())


@pytest.mark.parametrize("field,value", [
    ("name", None), ("brand", " "), ("product_id", "../escape"),
    ("price", True), ("price", "10"), ("price", -1),
    ("price", float("nan")), ("price", float("inf")), ("specifications", {}),
])
def test_invalid_catalog_values_are_quarantined_before_embedding(tmp_path, product, field, value):
    product[field] = value
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(product))
    with patch("src.ingestion.watcher.embed") as embed:
        assert ingest_file(path, failed_dir=tmp_path / "failed", debounce_s=0) is None
    embed.assert_not_called()
    assert field in (tmp_path / "failed/bad.json.error.txt").read_text()


def test_catalog_and_valid_inbox_fixtures_have_unique_valid_ids():
    paths = list((ROOT / "data/products").glob("*.json"))
    paths += list((ROOT / "data/ingestion-fixtures").glob("valid_*.json"))
    ids = []
    for path in paths:
        product = json.loads(path.read_text())
        assert validate_product(product) is None, path.name
        ids.append(product["product_id"])
    assert len(ids) == len(set(ids))


def test_duplicate_delivery_and_replacement_keep_the_same_document_id(tmp_path, product):
    path = tmp_path / "product.json"
    with patch("src.ingestion.watcher.embed", return_value=[[0.1]]) as embed, patch("src.ingestion.watcher.add") as add:
        for price in (89, 89, 95):
            product["price"] = price
            path.write_text(json.dumps(product))
            assert ingest_file(path, failed_dir=tmp_path / "failed", debounce_s=0) == product["product_id"]
    assert embed.call_count == 3
    assert all(call.kwargs["ids"] == [product["product_id"]] for call in add.call_args_list)
    assert "$95.00" in add.call_args.kwargs["documents"][0]
