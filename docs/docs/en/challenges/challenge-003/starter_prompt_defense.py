"""Challenge 003 starter: defend a RAG-style agent from prompt injection.

Goal: make all tests in test_prompt_defense.py pass.
Use only the Python standard library.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DOCUMENTS_PATH = Path(__file__).with_name("documents.json")
REQUESTS_PATH = Path(__file__).with_name("requests.json")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    """Normalize text for policy checks."""
    # Broken: too weak for mixed-case and punctuation-heavy attacks.
    return text


def detect_prompt_injection(text: str) -> bool:
    """Return True when text contains prompt-injection intent."""
    # Broken: catches only one exact phrase.
    return "ignore previous instructions" in text


def sanitize_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only context that is safe to use as policy evidence."""
    # Broken: trusts all imported documents.
    return documents


def should_answer(user_request: str) -> bool:
    """Return False when the user request should be blocked."""
    # Broken: allows everything.
    return True


def answer_from_context(user_request: str, safe_documents: list[dict[str, Any]]) -> str:
    """Answer using only safe policy context."""
    # Broken: returns a generic answer that is not grounded.
    return "Returns are unlimited and admin_override=true."


def evaluate_defense(
    requests: list[dict[str, Any]],
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate blocking, safe-answer behavior, and leakage."""
    safe_documents = sanitize_documents(documents)
    blocked_attacks = 0
    allowed_safe = 0
    leakage_count = 0

    for item in requests:
        allowed = should_answer(item["text"])
        if item["expected"] == "block" and not allowed:
            blocked_attacks += 1
        if item["expected"] == "allow" and allowed:
            allowed_safe += 1

        if allowed:
            answer = answer_from_context(item["text"], safe_documents).lower()
            if "admin_override" in answer or "system prompt" in answer or "unlimited" in answer:
                leakage_count += 1

    return {
        "blocked_attacks": blocked_attacks,
        "allowed_safe": allowed_safe,
        "leakage_count": leakage_count,
        "safe_docs": [doc["id"] for doc in safe_documents],
    }


def run_suite(
    documents_path: Path = DOCUMENTS_PATH,
    requests_path: Path = REQUESTS_PATH,
) -> dict[str, Any]:
    return evaluate_defense(load_json(requests_path), load_json(documents_path))


if __name__ == "__main__":
    print(json.dumps(run_suite(), indent=2))
