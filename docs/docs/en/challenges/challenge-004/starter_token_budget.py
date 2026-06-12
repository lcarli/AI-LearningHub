"""Challenge 004 starter: optimize prompts for a strict token budget.

Goal: make all tests in test_token_budget.py pass.
Use only the Python standard library.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DOCS_PATH = Path(__file__).with_name("context_docs.json")
REQUESTS_PATH = Path(__file__).with_name("requests.json")

STOP_WORDS = {"a", "after", "an", "and", "can", "does", "how", "i", "in", "is", "the", "to", "what"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def estimate_tokens(text: str) -> int:
    """Estimate tokens with a deterministic word-like tokenizer."""
    # Broken: character count is not a useful token estimate here.
    return len(text)


def keywords(text: str) -> set[str]:
    """Return normalized keywords for ranking."""
    # Broken: punctuation and stop words remain.
    return set(text.lower().split())


def rank_documents(question: str, docs: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Rank documents by relevance and compactness."""
    q = keywords(question)
    ranked = []
    for doc in docs:
        doc_terms = keywords(doc["title"] + " " + doc["text"])
        overlap = len(q & doc_terms)
        # Broken: longer docs win even when a short summary has same evidence.
        score = overlap + estimate_tokens(doc["text"]) / 100
        ranked.append({**doc, "score": score})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def select_context(
    question: str,
    docs: list[dict[str, str]],
    *,
    max_context_tokens: int,
) -> list[dict[str, str]]:
    """Select relevant context without exceeding max_context_tokens."""
    selected: list[dict[str, str]] = []
    used = 0
    for doc in rank_documents(question, docs):
        tokens = estimate_tokens(doc["text"])
        # Broken: ignores the budget.
        selected.append(doc)
        used += tokens
    return selected


def build_prompt(
    question: str,
    context: list[dict[str, str]],
    *,
    max_prompt_tokens: int,
) -> str:
    """Build a compact grounded-answer prompt under max_prompt_tokens."""
    context_text = "\n".join(f"[{doc['id']}] {doc['text']}" for doc in context)
    prompt = (
        "You are OutdoorGear support. Answer only from context.\n"
        f"Context:\n{context_text}\n"
        f"Question: {question}\n"
        "Answer:"
    )
    return prompt


def evaluate_budget(
    requests: list[dict[str, Any]],
    docs: list[dict[str, str]],
) -> dict[str, Any]:
    """Evaluate selected docs and prompt budget compliance."""
    selected_docs: list[str | None] = []
    all_under_budget = True

    for item in requests:
        context = select_context(item["question"], docs, max_context_tokens=35)
        selected_docs.append(context[0]["id"] if context else None)
        prompt = build_prompt(item["question"], context, max_prompt_tokens=item["max_prompt_tokens"])
        if estimate_tokens(prompt) > item["max_prompt_tokens"]:
            all_under_budget = False

    return {
        "selected_docs": selected_docs,
        "within_budget": selected_docs == [item["expected_doc_id"] for item in requests],
        "all_prompts_under_budget": all_under_budget,
    }


def run_budget_suite(
    docs_path: Path = DOCS_PATH,
    requests_path: Path = REQUESTS_PATH,
) -> dict[str, Any]:
    return evaluate_budget(load_json(requests_path), load_json(docs_path))


if __name__ == "__main__":
    print(json.dumps(run_budget_suite(), indent=2))
