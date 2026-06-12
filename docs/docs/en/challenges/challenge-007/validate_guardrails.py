"""Generate the completion code for Challenge 007.

Run after your implementation passes the tests:
    python validate_guardrails.py
"""

from __future__ import annotations

import hashlib
import json

from starter_guardrails import run_guardrail_suite


def completion_code() -> str:
    metrics = run_guardrail_suite()
    payload = {
        "challenge": "007-guardrails-red-team",
        "allowed": metrics["allowed"],
        "blocked": metrics["blocked"],
        "redacted": metrics["redacted"],
        "false_positive": metrics["false_positive"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH007-{digest}"


if __name__ == "__main__":
    print(completion_code())
