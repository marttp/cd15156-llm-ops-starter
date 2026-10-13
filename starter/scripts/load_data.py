"""Bootstrap the product corpus into Chroma.

Usage:
    uv run --no-project python scripts/load_data.py
    # or: make load-data
"""

import json
from pathlib import Path

from src.vectordb.chunker import chunk_product
from src.vectordb.embedder import embed
from src.vectordb.store import add
from src.ingestion.watcher import validate_product
from src.cache.semantic import clear as clear_answer_cache


def main() -> None:
    products_dir = Path("data/products")
    files = sorted(products_dir.glob("*.json"))
    print(f"Loading {len(files)} products into Chroma...")

    all_texts, all_metadatas, all_ids = [], [], []

    for path in files:
        product = json.loads(path.read_text())
        if reason := validate_product(product):
            raise ValueError(f"{path}: {reason}")
        if product["product_id"] in all_ids:
            raise ValueError(f"{path}: duplicate product_id {product['product_id']}")
        chunks = chunk_product(product)
        for chunk in chunks:
            all_texts.append(chunk["text"])
            all_metadatas.append(chunk["metadata"])
            all_ids.append(chunk["metadata"]["product_id"])

    embeddings = embed(all_texts)
    add(documents=all_texts, embeddings=embeddings, metadatas=all_metadatas, ids=all_ids)
    clear_answer_cache()

    print(f"Done — {len(all_ids)} chunks upserted.")


if __name__ == "__main__":
    main()
