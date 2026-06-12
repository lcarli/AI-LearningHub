"""Generate the completion code for Challenge 006.

Run after your implementation passes the tests:
    python validate_observability.py
"""

from __future__ import annotations

import hashlib
import json

from starter_observability import run_incident_summary


def completion_code() -> str:
    summary = run_incident_summary()
    payload = {
        "challenge": "006-observability-incident",
        "incident_trace": summary["incident_trace"],
        "root_cause": summary["root_cause"],
        "error_rate_pct": summary["error_rate_pct"],
        "p95_latency_ms": summary["p95_latency_ms"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH006-{digest}"


if __name__ == "__main__":
    print(completion_code())
