"""Generate the completion code for Challenge 004.

Run after your implementation passes the tests:
    python validate_token_budget.py
"""

from __future__ import annotations

import hashlib
import json

from starter_token_budget import DOCS_PATH, REQUESTS_PATH, evaluate_budget, load_json


def completion_code() -> str:
    metrics = evaluate_budget(load_json(REQUESTS_PATH), load_json(DOCS_PATH))
    payload = {
        "challenge": "004-token-budget",
        "selected_docs": metrics["selected_docs"],
        "within_budget": metrics["within_budget"],
        "all_prompts_under_budget": metrics["all_prompts_under_budget"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH004-{digest}"


if __name__ == "__main__":
    print(completion_code())
