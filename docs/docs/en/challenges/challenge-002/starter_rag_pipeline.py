"""Challenge 002 starter: fix a broken local RAG pipeline.

Goal: make all tests in test_rag_pipeline.py pass.
Use only the Python standard library.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DOCUMENTS_PATH = Path(__file__).with_name("documents.json")
QUERIES_PATH = Path(__file__).with_name("queries.json")

STOP_WORDS = {
    "a", "an", "and", "are", "at", "by", "can", "does", "for", "how",
    "i", "in", "is", "it", "of", "on", "or", "the", "to", "what", "with",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def tokenize(text: str) -> list[str]:
    """Return normalized search tokens."""
    # Broken: punctuation and stop words are not handled.
    return text.lower().split()


def chunk_documents(
    documents: list[dict[str, str]],
    *,
    max_words: int = 35,
    overlap: int = 5,
) -> list[dict[str, Any]]:
    """Split documents into searchable chunks while preserving source metadata."""
    # Broken: this returns one whole document per chunk and ignores max_words.
    return [
        {
            "chunk_id": doc["id"],
            "doc_id": doc["id"],
            "title": doc["title"],
            "text": doc["text"],
        }
        for doc in documents
    ]


def score_chunk(query: str, chunk: dict[str, Any]) -> float:
    """Score one chunk for a query."""
    # Broken: raw substring counting overweights common words.
    query_terms = query.lower().split()
    text = (chunk["title"] + " " + chunk["text"]).lower()
    return sum(text.count(term) for term in query_terms)


def retrieve(
    query: str,
    chunks: list[dict[str, Any]],
    *,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Return top chunks sorted from most to least relevant."""
    scored = [{**chunk, "score": score_chunk(query, chunk)} for chunk in chunks]
    # Broken: lowest scores come first.
    return sorted(scored, key=lambda item: item["score"])[:top_k]


def answer_question(query: str, retrieved: list[dict[str, Any]]) -> str:
    """Create a concise grounded answer from retrieved chunks."""
    # Broken: this does not use the retrieved evidence.
    return "I do not have enough information in the retrieved context."


def evaluate(
    queries: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate retrieval and answer coverage for the provided queries."""
    top_docs: list[str | None] = []
    covered = 0

    for item in queries:
        retrieved = retrieve(item["query"], chunks, top_k=3)
        top_doc = retrieved[0]["doc_id"] if retrieved else None
        top_docs.append(top_doc)
        answer = answer_question(item["query"], retrieved).lower()
        if all(term.lower() in answer for term in item["required_terms"]):
            covered += 1

    # Broken: denominator should be the number of queries.
    return {
        "top_docs": top_docs,
        "top1_accuracy": 0.0,
        "required_coverage": covered / max(len(chunks), 1),
    }


def run_pipeline(
    documents_path: Path = DOCUMENTS_PATH,
    queries_path: Path = QUERIES_PATH,
) -> dict[str, Any]:
    documents = load_json(documents_path)
    queries = load_json(queries_path)
    chunks = chunk_documents(documents)
    return evaluate(queries, chunks)


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
