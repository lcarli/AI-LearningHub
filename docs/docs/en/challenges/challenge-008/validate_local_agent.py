"""Generate the completion code for Challenge 008.

Run after your implementation passes the tests:
    python validate_local_agent.py
"""

from __future__ import annotations

import hashlib
import json

from starter_local_agent import run_eval


def completion_code() -> str:
    metrics = run_eval()
    payload = {
        "challenge": "008-local-only-agent",
        "intents": metrics["intents"],
        "successful_requests": metrics["successful_requests"],
        "uses_cloud": metrics["uses_cloud"],
        "required_outputs": metrics["required_outputs"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH008-{digest}"


if __name__ == "__main__":
    print(completion_code())
