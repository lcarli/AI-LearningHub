"""Acceptance tests for Challenge 002.

Run:
    python -m pytest test_rag_pipeline.py
"""

from __future__ import annotations

from starter_rag_pipeline import (
    chunk_documents,
    answer_question,
    evaluate,
    load_json,
    retrieve,
    tokenize,
    DOCUMENTS_PATH,
    QUERIES_PATH,
)


def test_tokenize_normalizes_text_and_removes_stop_words():
    tokens = tokenize("Can I return a RainShell jacket after 45 days?")

    assert "rainshell" in tokens
    assert "45" in tokens
    assert "days" in tokens
    assert "can" not in tokens
    assert "i" not in tokens


def test_chunk_documents_preserves_metadata_and_limits_size():
    documents = load_json(DOCUMENTS_PATH)
    chunks = chunk_documents(documents, max_words=12, overlap=3)

    assert len(chunks) > len(documents)
    assert all({"chunk_id", "doc_id", "title", "text"} <= set(chunk) for chunk in chunks)
    assert all(len(chunk["text"].split()) <= 12 for chunk in chunks)
    assert {chunk["doc_id"] for chunk in chunks} == {doc["id"] for doc in documents}


def test_retrieve_returns_expected_top_document_for_each_query():
    documents = load_json(DOCUMENTS_PATH)
    queries = load_json(QUERIES_PATH)
    chunks = chunk_documents(documents, max_words=35, overlap=5)

    top_docs = [retrieve(item["query"], chunks, top_k=3)[0]["doc_id"] for item in queries]

    assert top_docs == ["returns-rain", "camp-stove-fuel", "shipping-canada"]


def test_answer_question_uses_retrieved_context():
    documents = load_json(DOCUMENTS_PATH)
    chunks = chunk_documents(documents, max_words=35, overlap=5)
    retrieved = retrieve("What fuel does the SparkMini stove use?", chunks, top_k=3)

    answer = answer_question("What fuel does the SparkMini stove use?", retrieved).lower()

    assert "isobutane" in answer
    assert "canisters" in answer


def test_evaluate_reports_perfect_results_for_fixture_queries():
    documents = load_json(DOCUMENTS_PATH)
    queries = load_json(QUERIES_PATH)
    chunks = chunk_documents(documents, max_words=35, overlap=5)

    metrics = evaluate(queries, chunks)

    assert metrics["top_docs"] == ["returns-rain", "camp-stove-fuel", "shipping-canada"]
    assert metrics["top1_accuracy"] == 1.0
    assert metrics["required_coverage"] == 1.0
