"""Generate the completion code for Challenge 002.

Run after your implementation passes the tests:
    python validate_rag_pipeline.py
"""

from __future__ import annotations

import hashlib
import json

from starter_rag_pipeline import DOCUMENTS_PATH, QUERIES_PATH, chunk_documents, evaluate, load_json


def completion_code() -> str:
    documents = load_json(DOCUMENTS_PATH)
    queries = load_json(QUERIES_PATH)
    chunks = chunk_documents(documents, max_words=35, overlap=5)
    metrics = evaluate(queries, chunks)

    payload = {
        "challenge": "002-rag-pipeline",
        "top_docs": metrics["top_docs"],
        "top1_accuracy": metrics["top1_accuracy"],
        "required_coverage": metrics["required_coverage"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH002-{digest}"


if __name__ == "__main__":
    print(completion_code())
