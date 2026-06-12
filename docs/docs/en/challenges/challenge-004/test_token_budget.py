"""Acceptance tests for Challenge 004.

Run:
    python -m pytest test_token_budget.py
"""

from __future__ import annotations

from starter_token_budget import (
    DOCS_PATH,
    REQUESTS_PATH,
    build_prompt,
    estimate_tokens,
    evaluate_budget,
    keywords,
    load_json,
    rank_documents,
    select_context,
)


def test_estimate_tokens_counts_word_like_tokens():
    assert estimate_tokens("Returns are accepted within 60 days.") == 6
    assert estimate_tokens("5-8 business days after fulfillment") == 6


def test_keywords_normalize_and_remove_stop_words():
    terms = keywords("Can I return clean, unused gear after 45 days?")

    assert {"return", "clean", "unused", "gear", "45", "days"} <= terms
    assert "can" not in terms
    assert "i" not in terms


def test_rank_documents_prefers_relevant_short_summary():
    docs = load_json(DOCS_PATH)

    ranked = rank_documents("Can I return clean unused gear after 45 days?", docs)

    assert ranked[0]["id"] == "returns-short"
    assert ranked.index(next(doc for doc in ranked if doc["id"] == "returns-short")) < ranked.index(
        next(doc for doc in ranked if doc["id"] == "returns-long")
    )


def test_select_context_respects_context_budget():
    docs = load_json(DOCS_PATH)

    context = select_context("What fuel does SparkMini use?", docs, max_context_tokens=18)

    assert [doc["id"] for doc in context] == ["stove-short"]
    assert sum(estimate_tokens(doc["text"]) for doc in context) <= 18


def test_build_prompt_stays_under_budget():
    docs = load_json(DOCS_PATH)
    request = load_json(REQUESTS_PATH)[2]
    context = select_context(request["question"], docs, max_context_tokens=35)

    prompt = build_prompt(request["question"], context, max_prompt_tokens=request["max_prompt_tokens"])

    assert estimate_tokens(prompt) <= request["max_prompt_tokens"]
    assert "shipping-short" in prompt
    assert "brand-story" not in prompt


def test_evaluate_budget_reports_expected_results():
    metrics = evaluate_budget(load_json(REQUESTS_PATH), load_json(DOCS_PATH))

    assert metrics["selected_docs"] == ["returns-short", "stove-short", "shipping-short"]
    assert metrics["within_budget"] is True
    assert metrics["all_prompts_under_budget"] is True
