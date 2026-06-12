"""Generate the completion code for Challenge 003.

Run after your implementation passes the tests:
    python validate_prompt_defense.py
"""

from __future__ import annotations

import hashlib
import json

from starter_prompt_defense import DOCUMENTS_PATH, REQUESTS_PATH, evaluate_defense, load_json


def completion_code() -> str:
    metrics = evaluate_defense(load_json(REQUESTS_PATH), load_json(DOCUMENTS_PATH))
    payload = {
        "challenge": "003-prompt-injection",
        "blocked_attacks": metrics["blocked_attacks"],
        "allowed_safe": metrics["allowed_safe"],
        "leakage_count": metrics["leakage_count"],
        "safe_docs": metrics["safe_docs"][:2],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH003-{digest}"


if __name__ == "__main__":
    print(completion_code())
